from django.db import models

class Document(models.Model):
    """중앙/지자체 복지 정책 정보를 저장하는 모델."""
    service_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=500)
    description = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=20, choices=[("central", "중앙부처"), ("local", "지자체")])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """정책 제목 반환."""
        return self.title


