from rest_framework import serializers


class VerifyUserIn(serializers.Serializer):
    username = serializers.CharField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class VerifyUserOut(serializers.Serializer):
    valid = serializers.BooleanField(default=False, help_text='True: username not used, other is False')

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class RegisterIn(serializers.Serializer):
    username = serializers.CharField(max_length=128)
    password = serializers.CharField(max_length=128)
    email = serializers.EmailField(max_length=128, required=False)
    first_name = serializers.CharField(max_length=128, required=False)
    last_name = serializers.CharField(max_length=128, required=False)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class RegisterOut(serializers.Serializer):
    user = serializers.IntegerField(help_text='User ID')
    token = serializers.CharField(help_text='Token used to invoke API')
    refresh_token = serializers.CharField(help_text='Token used to refresh new API token')

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class LoginIn(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class RefreshJWTIn(serializers.Serializer):
    refresh_token = serializers.CharField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class RefreshJWTOut(serializers.Serializer):
    token = serializers.CharField()
    refresh_token = serializers.CharField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
