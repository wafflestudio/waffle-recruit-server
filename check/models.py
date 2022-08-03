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
    last_try = models.IntegerField(default=0)
    
    def __str__(self):
        return str(self.user.username)

class Submission(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    prob_num = models.PositiveSmallIntegerField()
    task_id = models.CharField(max_length=36)
    submit_at = models.DateTimeField(auto_now_add=True)
    finished = models.PositiveSmallIntegerField()