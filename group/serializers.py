from rest_framework import serializers


class GroupDetailIn(serializers.Serializer):
    number = serializers.IntegerField(help_text='Meeting call number')

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class GroupInfo(serializers.Serializer):
    id = serializers.IntegerField(help_text='group ID')
    name = serializers.CharField(help_text='group name')
    users = serializers.ListField(help_text='group members', child=serializers.IntegerField())

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class StartIn(GroupDetailIn):
    group = serializers.ListField(help_text='group information', child=GroupInfo())


class BaseOut(serializers.Serializer):
    success = serializers.BooleanField(default=True)

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class MoveMemberIn(GroupDetailIn):
    members = serializers.ListField(help_text='User ID who will be moved', child=serializers.IntegerField())
    from_group = serializers.IntegerField(help_text='From which group')
    to_group = serializers.IntegerField(help_text='To which group')


class GroupDetailOut(serializers.Serializer):
    group = serializers.ListField(help_text='group information', child=GroupInfo())

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass
