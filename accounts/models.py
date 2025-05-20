from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import BaseUserManager

class UserManager(BaseUserManager):
    """사용자 생성 및 관리 전용 매니저."""
    def create_user(self, email, password=None, **extra_fields):
        """이메일과 비밀번호로 일반 사용자 생성."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """관리자 권한을 가진 슈퍼유저 생성."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)
    

class User(AbstractUser):
    """커스텀 사용자 모델(이메일 기반)."""
    username = None
    first_name = None
    last_name = None
    email = models.EmailField(unique=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    region = models.CharField(max_length=50, null=True, blank=True)
    subregion = models.CharField(max_length=50, null=True, blank=True)

    REQUIRED_FIELDS = []
    USERNAME_FIELD = "email"

    objects = UserManager()

    def __str__(self):
        """이메일 문자열 반환."""
        return self.email
