from django.contrib.auth.models import User
from rest_framework import serializers


class UserInfoOut(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')


class ChangePwdIn(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ChangePwdOut(serializers.Serializer):
    success = serializers.BooleanField(default=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class UpdateUserInfoIn(serializers.Serializer):
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(max_length=128, required=False)
    last_name = serializers.CharField(max_length=128, required=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
