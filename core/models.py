from django.db import models
from django.contrib.auth.models import User

class QuizAttempt(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attempts')
    topic = models.CharField(max_length=255)
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=30)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.topic} - {self.score}/{self.total_questions}"

class QuizQuestion(models.Model):
    attempt = models.ForeignKey(QuizAttempt, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_answer = models.CharField(max_length=1) # A, B, C, or D
    selected_answer = models.CharField(max_length=1, blank=True, null=True)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return f"Question for {self.attempt.topic}"
