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
from django.shortcuts import redirect, reverse
import requests
import os


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


class GithubSigninService(serializers.Serializer):
    def execute(self):
        request = self.context.get("request")
        client_id = os.getenv("GITHUB_CLIENT_ID")
        redirect_uri = "https://recruit2022-api.wafflestudio.com/auth/signin/github/callback/"
        # redirect_uri = "http://localhost:8000/auth/signin/github/callback/"
        return redirect(
                f"https://github.com/login/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}&scope=read:user"
            )
    

class GithubCallbackService(serializers.Serializer):
    code = serializers.CharField()

    def validate(self, data):
        self.context["code"] = data.get("code", None)
        if self.context["code"] is None:
            raise AuthenticationFailed("깃허브 로그인이 정상적으로 진행되지 않았습니다.")
        return data

    def execute(self):
        request = self.context.get("request")
        client_id = os.getenv("GITHUB_CLIENT_ID")
        client_secrets = os.getenv("GITHUB_CLIENT_SECRETS")
        code = self.context.get("code")
        result = requests.post(
            f"https://github.com/login/oauth/access_token?client_id={client_id}&client_secret={client_secrets}&code={code}",
            headers={"Accept": "application/json"}
        ).json()
        if hasattr(result, "error"):
            return AuthenticationFailed("깃허브 로그인이 정상적으로 진행되지 않았습니다.")
        access_token = result.get("access_token")
        user_profile = requests.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"token {access_token}",
                "Accept": "application/json"
            }
        ).json()

        # user = User.objects.get_or_create(username=user_profile.get("login"), email=user_profile.get("email"))[0]
        user = User.objects.get(username=user_profile.get("login"), email=user_profile.get("email"))
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

