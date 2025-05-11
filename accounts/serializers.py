from rest_framework import serializers
from .models import User

class SignupSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("username", "email", "password", "age", "region", "subregion")

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("username", "email", "age", "region", "subregion")
        read_only_fields = ("username", "email")