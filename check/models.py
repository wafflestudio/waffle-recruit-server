from django.conf import settings
from django.db import models
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta

User = get_user_model()

class Solver(models.Model):
    class Meta:
        unique_together = (('user', 'prob_num'),)
    prob_num = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    solved_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return str(self.user.username)


#[TODO] Model for db logging - 틀린 경우 유저, 문항, 제출시간, 결과물을 저장할 예정
class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prob_num = models.PositiveSmallIntegerField()
    task_id = models.CharField(max_length=36)
    submit_at = models.DateTimeField(auto_now_add=True)
    result = models.TextField(null=True)