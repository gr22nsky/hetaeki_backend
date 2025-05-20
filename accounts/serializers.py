from rest_framework import serializers
from .models import User

class SignupSerializer(serializers.ModelSerializer):
    """회원가입용 사용자 직렬화기."""
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "password", "age", "region", "subregion")

    def create(self, validated_data):
        """UserManager를 통해 사용자 생성."""
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """프로필 조회/수정용 직렬화기."""
    class Meta:
        model = User
        fields = ("email", "age", "region", "subregion")
        read_only_fields = ["email"]