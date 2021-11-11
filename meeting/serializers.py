from rest_framework import serializers

from meeting.models import Meeting


class BaseSerializer(serializers.Serializer):
    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class NewMeetingIn(BaseSerializer):
    name = serializers.CharField(max_length=128)
    begin_at = serializers.DateTimeField()
    end_at = serializers.DateTimeField()
    mute_type = serializers.ChoiceField(choices=Meeting.MuteType.choices, required=False)
    password = serializers.CharField(required=False)


class NewMeetingOut(serializers.ModelSerializer):
    number = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = ('number', 'created')

    def get_number(self, obj):
        return obj.call_number


class BaseMeetingOut(BaseSerializer):
    success = serializers.BooleanField()


class MeetingInfoIn(BaseSerializer):
    number = serializers.IntegerField(help_text='Call number of meeting')


class MeetingInfoOut(serializers.ModelSerializer):
    owner_id = serializers.SerializerMethodField()
    owner_name = serializers.SerializerMethodField()
    number = serializers.SerializerMethodField()

    class Meta:
        model = Meeting
        fields = ('name', 'number', 'password', 'owner_name', 'owner_id', 'status', 'begin_at', 'end_at')

    def get_owner_name(self, obj):
        if obj.owner is None:
            return None
        return obj.owner.username

    def get_owner_id(self, obj):
        if obj.owner is None:
            return None
        return obj.owner.id

    def get_number(self, obj):
        return obj.call_number


class MeetingListIn(BaseSerializer):
    beginAt = serializers.DateTimeField(required=False, help_text='Time with zone, etc: 2021-08-12T07:56:41+08:00')
    endAt = serializers.DateTimeField(required=False)


class DelMeetingIn(BaseSerializer):
    meetings = serializers.ListField(child=serializers.IntegerField(), help_text="list of meeting' number to delete")


class JoinMeetingIn(BaseSerializer):
    number = serializers.IntegerField()
    password = serializers.CharField(required=False)


class MeetingIn(BaseSerializer):
    number = serializers.IntegerField()


class JoinMeetingOut(BaseSerializer):
    token = serializers.CharField()
    app_key = serializers.CharField()
    room_id = serializers.IntegerField()
    share_user_id = serializers.IntegerField()
    share_user_token = serializers.CharField()
    is_breakout = serializers.BooleanField(default=False)
