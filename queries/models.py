from django.db import models
from django.conf import settings

class UserQuery(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="queries")
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"[{self.user.email}] {self.question[:30]}"


class HotTopic(models.Model):
    AGE_GROUP_CHOICES = [
        ("teen", "청소년"),   # 10대 이하
        ("youth", "청년"),   # 20~30대
        ("middle", "장년"),  # 40~50대
        ("senior", "노년"),  # 60대 이상
    ]

    age_group = models.CharField(max_length=10, choices=AGE_GROUP_CHOICES)
    topics = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_age_group_display()} - {self.created_at.date()}"