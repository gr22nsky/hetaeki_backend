from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    region = models.CharField(max_length=50, null=True, blank=True)
    subregion = models.CharField(max_length=50, null=True, blank=True)

    REQUIRED_FIELDS = ["email"]
    USERNAME_FIELD = "username"

    def __str__(self):
        return self.username
