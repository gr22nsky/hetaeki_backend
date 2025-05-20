from django.db import models
from django.conf import settings

class UserQuery(models.Model):
    """사용자 질문 및 GPT 응답 기록 모델."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="queries")
    question = models.TextField()
    answer = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """이메일과 질문 일부를 문자열로 반환."""
        return f"[{self.user.email}] {self.question[:30]}"


class HotTopic(models.Model):
    """연령대별 인기 질문 주제 모델."""
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
        """연령대와 생성일을 문자열로 반환."""
        return f"{self.get_age_group_display()} - {self.created_at.date()}"