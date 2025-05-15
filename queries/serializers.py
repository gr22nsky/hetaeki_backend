from rest_framework import serializers
from .models import UserQuery

class UserQuerySerializer(serializers.ModelSerializer):
    class Meta:
        model = UserQuery
        fields = ["id", "user", "question", "answer", "created_at"]
        read_only_fields = ["id", "answer", "created_at"]