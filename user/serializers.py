from rest_framework import serializers
from utils.tokens import AccessToken, RefreshToken, jwt_token_of
from .models import User
from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from django.db import transaction
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
import hashlib
from django.db.transaction import atomic


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "username", "major", "grade")
        extra_kwargs = {"password": {"write_only": True}}
    
    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("이미 존재하는 이메일입니다.")
        return value
    
    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("이미 존재하는 이름입니다.")
        return value

    def update(self, instance, validated_data):
        instance.email = validated_data.get("email", instance.email)
        instance.username = validated_data.get("username", instance.username)
        instance.major = validated_data.get("major", instance.major)
        instance.grade = validated_data.get("grade", instance.grade)
        instance.save()

        return instance


class SignupService(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "username", "password", "major", "grade")
        extra_kwargs = {"password": {"write_only": True}}

    @atomic
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        user.save()
        user_data = UserSerializer(user).data

        return user_data, jwt_token_of(user)
    

class SigninService(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    
    def validate(self, data):
        username= data.get("username", None)
        password = data.get("password", None)
        user = authenticate(username=username, password=password)

        if user is None:
            raise AuthenticationFailed("아이디 또는 비밀번호를 확인하세요.")
        self.context["user"] = user

        return data
    
    def execute(self):
        user = self.context.get("user")
        update_last_login(None, user)
        user_data = UserSerializer(user).data

        return user_data, jwt_token_of(user)


class SignoutService(serializers.Serializer):
    refresh = serializers.CharField()

    def validate_refresh(self, value):
        try:
            RefreshToken(value)
        except TokenError:
            raise serializers.ValidationError("유효하지 않은 토큰입니다.")

        return value

    @transaction.atomic
    def execute(self):
        refresh_token = RefreshToken(self.validated_data.get("refresh"))
        refresh_token.blacklist()

        request = self.context.get("request")
        access_token = AccessToken(request.META.get("HTTP_AUTHORIZATION").split()[1])
        access_token.blacklist()

        return True

class RefreshService(SignoutService, TokenRefreshSerializer):
    token_class = RefreshToken

    def execute(self):
        return {"access": self.validated_data.get("access")}

