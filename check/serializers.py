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
SUBMISSION_DUE = datetime.strptime("2022-08-30 00:00:00", "%Y-%m-%d %H:%M:%S")  # 8/19 00:00:30 KST (UTC+9)

LANGUAGE_CHOICES = (
    ('c++', 'c++'),
    ('python', 'python'),
    ('java', 'java'),
    ('javascript', 'javascript'),
    ('kotlin', 'kotlin'),
)

FILTER = {
    "common": ["sudo", "gksudo", "rm -rf"],
    "c++": ["system(", "popen(", "fork(", "waitpid("], ## typescript -> cpp
    "python": ["__import__", "import os", "import subprocess", "import sys", "from os", "from subprocess","from sys",
    ".system(", ".popen(", "exec(", "importlib", "import_module"],
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
        if prob_num < 0 or prob_num > 3:
            raise serializers.ValidationError("없는 문제 번호입니다.")

        if datetime.now() > SUBMISSION_DUE:
            raise serializers.ValidationError("제출기간이 지났습니다.")

        last_submit = Submission.objects.filter(user=user).order_by('-submit_at').first()

        if last_submit is not None and last_submit.submit_at + timedelta(seconds=30) > datetime.now():
            time_remain = timedelta(seconds=30) - (datetime.now() - last_submit.submit_at)
            raise AuthenticationFailed({
                "remain": int(time_remain.total_seconds())
            })
        self.context['last_submit'] = last_submit
        return data
    
    def execute(self):
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
                return Response({"error": f"제출 실패. 다음 표현은 사용 불가합니다: {filtered}"}, status=400)
            if '..' in file['filename']:
                return Response({"error": "invalid filename: `..` is not allowed"}, status=400)
            
            local_file = open(file_path + file['filename'], 'w')
            local_file.write(file['code'])
            local_file.close()
        with open(file_path + json_filename, 'w') as local_file:
            json.dump(req_data, local_file)

        task: AsyncResult = run_solver.delay(language, user_id, prob_num=prob_num)
        Submission.objects.create(user=user, task_id=task.id, prob_num=prob_num, finished=0)
        return Response({"msg": "제출이 완료되었습니다."}, status=201)


class ResultService(serializers.Serializer):
    def validate(self, data):
        user = self.context['request'].user
        prob_num = self.context['prob_num']
        if not Submission.objects.filter(user=user, prob_num=prob_num).exists():
            raise serializers.ValidationError("제출하지 않은 문제입니다.")
        return data

    def execute(self):
        validated_data = self.validated_data
        user = self.context['request'].user
        prob_num = self.context['prob_num']
        
        already_solved=False
        solver_obj = Solver.objects.filter(user=user, prob_num=prob_num)
        if solver_obj.exists():
            solver_obj= solver_obj.first()
            already_solved=True

        submission_obj = Submission.objects.filter(user=user, prob_num=prob_num).order_by('-submit_at').first()
        task = AsyncResult(submission_obj.task_id)

        msg = {}
        if task.ready(): # 채점이 끝났으면
            submission_obj.finished=1 # 끝났다고 이야기해주고
            submission_obj.save() # 저장
            solved, original_prob_num, error = task.result
            task.forget() # 태스크 지워주고 -> mry 관리에서 중요하다고 함
            if solved and not already_solved: # 지금 맞았고, 기존에 맞춘 적 없었으면
                Solver.objects.create(user=user, prob_num=prob_num, last_try=1)
                msg = { "result": 1, "last_try": 1 } 
            elif solved and already_solved: # 지금 맞았고, 기존에 맞춘 적 있었으면
                solver_obj.last_try=1 
                solver_obj.save()
                msg = { "result": 1, "last_try": 1 }
            elif not solved and already_solved: # 지금 틀렸고, 기존에 맞춘 적 있었으면
                solver_obj.last_try=0 
                solver_obj.save()
                msg = { "result": 1, "last_try": 0 }
            elif not solved and not already_solved: # 지금 틀렸고, 기존에도 틀렸으면
                msg = { "result": 0, "last_try": 0 }
        else:
            if not (submission_obj.finished) : # 채점 안끝났음
                if not already_solved : # 푼적 없으면
                    msg = {"result": 0, "last_try": -1}             
                else: # 푼적 있으면
                    msg = {"result": 1, "last_try": -1}
            else: # 채점 끝났음, 기존에 풀었고 task는 지워진지 오래
                if not already_solved : # 틀렸으면 -> 여기로는 오면 안되는데 기존에 회원때매 일단 둠
                    msg = { "result": 0, "last_try": 0} # -2 for exceptional case
                else:
                    msg = {"result": 1, "last_try": solver_obj.last_try}
        return Response(msg, status=200)

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


class LoadTestService(serializers.Serializer):

    def validate(self, data):
        return data

    def execute(self):
        return Response({"msg": "only for test purpose"}, status=401)
        validated_data = self.validated_data
        user_id = "loadtest_user01"
        prob_num = "1"
        req_data = {
                "language": "python",
                "files": [{
                    "filename": "main.py",
                    "code": "import time;time.sleep(3)"
                }]
        }
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
            test_filename = file['filename'].replace("index.ts", "main.cpp") 
            local_file = open(file_path + test_filename, 'w')
            local_file.write(file['code'])
            local_file.close()
        with open(file_path + json_filename, 'w') as local_file:
            json.dump(req_data, local_file)

        task: AsyncResult = run_solver.delay(language, user_id, prob_num=prob_num)
        Submission.objects.create(user=user, task_id=task.id, prob_num=prob_num)
        return Response({"msg": "제출이 완료되었습니다."}, status=201)
