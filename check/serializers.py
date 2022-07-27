from genericpath import exists
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from .models import Solver, Submission 
from .tasks import run_solver
from datetime import datetime, timedelta, timezone
from celery.result import AsyncResult
import shutil
import os

import hashlib
import json
import boto3

from django.conf import settings

json_filename = "juys8J1swR_solution.json"
response_json_filename = "juys8J1swR_response.json"
saved_indicator = "SAVED_IN_FILE"
SUBMISSION_DUE = datetime.strptime("2022-07-30 00:00:00", "%Y-%m-%d %H:%M:%S")  # 8/19 00:00:30 KST (UTC+9)

LANGUAGE_CHOICES = (
    ('c++', 'c++'),
    ('python', 'python'),
    ('java', 'java'),
    ('javascript', 'javascript'),
    ('kotlin', 'kotlin'),
)

FILTER = {
    "common": ["sudo", "gksudo", "rm -rf"],
    "typescript": ["system(", "popen(", "fork(", "waitpid("], ## typescript -> cpp
    "python": ["__import__", "import os", "import subprocess", "import sys", "from os", "from subprocess","from sys",
    ".system(", ".popen(", "exec(", "eval("],
    "java": ["Runtime.", ".getRuntime(", ".exec(", "ProcessBuilder", "System.getProperty("],
    "javascript": ["exec(", "child_process", "spawn("],
    "kotlin": ["shellRun", "ShellLocation", "Runtime.", "getRuntime(", "exec(", "ProcessBuilder", ".command(", "Shell("]
}

class SubmissionService(serializers.Serializer):
    req_data = serializers.JSONField(required=True)

    def _filtering(self, lang, code):
        filter_list = FILTER[lang] + FILTER["common"]
        for stopword in filter_list:
            if stopword in code:
                return False, stopword
        return True, ""

    def validate(self, data):
        user = self.context['request'].user
        prob_num = self.context['prob_num']
        print("prob_num: ", prob_num)
        if prob_num < 1 or prob_num > 10:
            raise serializers.ValidationError("없는 문제 번호입니다.")

        if Solver.objects.filter(user=user, prob_num=prob_num).exists():
            raise serializers.ValidationError("이미 맞춘 문제입니다.")

        if datetime.now() > SUBMISSION_DUE:
            raise serializers.ValidationError("제출기간이 지났습니다.")

        last_submit = Submission.objects.filter(user=user).order_by('-submit_at').first()
        if last_submit is not None:
            if last_submit.submit_at + timedelta(seconds=10) > datetime.now():
                time_remain = timedelta(seconds=10) - (datetime.now() - last_submit.submit_at)
                raise AuthenticationFailed({
                    "remain": int(time_remain.total_seconds())
                })
        self.context['last_submit'] = last_submit
        return data
    
    def execute(self):
        # self._get_free_container()
        validated_data = self.validated_data
        user = self.context['request'].user
        user_id = "user"+str(user.id)
        prob_num = self.context['prob_num']
        last_submit = self.context.get('last_submit', None)
        req_data = validated_data['req_data']
        if last_submit is not None:
            _task = AsyncResult(last_submit.task_id)
            _task.revoke()
            _task.forget()
        file_path = f"codes/{user_id}/{prob_num}/"
        
        try:
            shutil.rmtree(file_path)
        except Exception:
            pass
        try:
            os.makedirs(file_path)
        except Exception:
            pass

        files = req_data['files']
        language = req_data['language']
        for file in files:
            (res, filtered) = self._filtering(language, file['code'])
            if res==False:
                return Response({f"제출 실패. 다음 표현은 사용 불가합니다: {filtered}"}, status=400)
            if '..' in file['filename']:
                return Response({"error": "invalid filename: `..` is not allowed"}, status=400)
            
            # [TODO] Replace typescript with cpp
            # (daeyong) 임시방편으로 ts파일을 main.cpp로 강제변환중.
            test_filename = file['filename'].replace("index.ts", "main.cpp") 
            local_file = open(file_path + test_filename, 'w')
            #local_file = open(file_path + file['filename'], 'w')
            local_file.write(file['code'])
            local_file.close()
        with open(file_path + json_filename, 'w') as local_file:
            json.dump(req_data, local_file)

        task: AsyncResult = run_solver.delay(language, user_id, prob_num=prob_num)
        Submission.objects.create(user=user, task_id=task.id, prob_num=prob_num)
        return Response("제출이 완료되었습니다.", status=201)


class ResultService(serializers.Serializer):
    def validate(self, data):
        user = self.context['request'].user
        prob_num = self.context['prob_num']
        if not Submission.objects.filter(user=user, prob_num=prob_num).exists():
            raise serializers.ValidationError("제출하지 않은 문제입니다.")
        return data

    def execute(self):
        validated_data = self.validated_data
        # [TODO] Result랑 Submission 모델 정리하고 다시 생각
        # 결과 확인용으로 임시로 만듬
        # 새로 풀면 어케 할지 고민
        # 예외처리 아예 안되어있음
        user = self.context['request'].user
        prob_num = self.context['prob_num']
        
        solver_obj = Solver.objects.filter(user=user, prob_num=prob_num)
        if solver_obj.exists():
            return Response({"result": "맞음 (from solver obj)"}, status=200)

        submission_obj = Submission.objects.filter(user=user, prob_num=prob_num).order_by('-submit_at').first()
        task = AsyncResult(submission_obj.task_id)
        if task.ready():
            solved, original_prob_num, error = task.result
            if solved:
                Solver.objects.create(user=user, prob_num=prob_num)
                task.forget()
                return Response({"result": "맞음 (from submission obj)"}, status=200)
            else:
                task.forget()
                return Response({"result": "틀림 (from submission obj)"}, status=200)

class SkeletonService(serializers.Serializer):
    lang = serializers.ChoiceField(choices=LANGUAGE_CHOICES, required=True)

    def validate(self, data):
        return data

    def execute(self):
        lang = self.validated_data['lang']
        client = boto3.client('s3')
        file_name = 'pr3_skel_{}.tar'.format(lang)
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        url = client.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': file_name, },
            ExpiresIn=600,
        )
        return Response({"url": url}, status=200)


