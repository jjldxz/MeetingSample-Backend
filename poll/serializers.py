from django.contrib.auth.models import User
from rest_framework import serializers

from poll.models import Poll, PollQuestion, PollOption


class PollListIn(serializers.Serializer):
    number = serializers.CharField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PollListOut(serializers.ModelSerializer):
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Poll
        exclude = ('deleted', 'round', 'meeting')

    def get_question_count(self, obj):
        return PollQuestion.objects.filter(poll=obj).count()


class OptionIn(serializers.ModelSerializer):
    class Meta:
        model = PollOption
        exclude = ('deleted', 'question')


class QuestionIn(serializers.ModelSerializer):
    options = serializers.ListField(child=OptionIn())

    class Meta:
        model = PollQuestion
        exclude = ('deleted', 'poll')


class OptionOut(serializers.ModelSerializer):
    id = serializers.IntegerField()

    class Meta:
        model = PollOption
        exclude = ('deleted', 'question')


class QuestionOut(serializers.ModelSerializer):
    id = serializers.IntegerField()
    options = serializers.ListField(child=OptionOut())

    class Meta:
        model = PollQuestion
        exclude = ('deleted', 'poll')


class PollDetailOut(serializers.ModelSerializer):
    questions = serializers.ListField(child=QuestionOut())

    class Meta:
        model = Poll
        exclude = ('deleted', 'round')


class PollNewIn(serializers.ModelSerializer):
    number = serializers.IntegerField()
    questions = serializers.ListField(child=QuestionIn())

    class Meta:
        model = Poll
        exclude = ('id', 'meeting', 'deleted', 'round', 'status', 'share')


class PollUpdateIn(serializers.ModelSerializer):
    id = serializers.IntegerField()
    questions = serializers.ListField(child=QuestionIn())

    class Meta:
        model = Poll
        fields = ('id', 'title', 'questions', 'is_anonymous')


class PollIn(serializers.Serializer):
    id = serializers.IntegerField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class Voter(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username')


class OptionResult(serializers.Serializer):
    content = serializers.CharField()
    count = serializers.IntegerField()
    voters = serializers.ListField(required=False, child=Voter())

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class QuestionResult(serializers.Serializer):
    is_single = serializers.BooleanField(required=False)
    content = serializers.CharField()
    options = serializers.ListField(child=OptionResult())

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PollResultOut(serializers.Serializer):
    title = serializers.CharField()
    is_anonymous = serializers.BooleanField()
    status = serializers.IntegerField()
    voter_num = serializers.IntegerField(required=False)
    questions = serializers.ListField(child=QuestionResult())

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PollCommitOption(serializers.Serializer):
    id = serializers.IntegerField(help_text='Option ID')

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PollCommitQuestion(serializers.Serializer):
    id = serializers.IntegerField(help_text='Question ID')
    options = serializers.ListField(child=PollCommitOption())

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PollCommitIn(serializers.Serializer):
    poll_id = serializers.IntegerField(help_text='Poll ID')
    questions = serializers.ListField(child=PollCommitQuestion())

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PollCommitOut(serializers.Serializer):
    poll_id = serializers.IntegerField(help_text='Poll ID')
    round = serializers.IntegerField(help_text='Round of poll')

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PollStartOut(serializers.ModelSerializer):
    class Meta:
        model = Poll
        exclude = ('deleted',)


class OptionAnswer(serializers.Serializer):
    content = serializers.CharField()
    select = serializers.BooleanField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class QuestionAnswer(serializers.Serializer):
    content = serializers.CharField()
    options = serializers.ListField(child=OptionAnswer())
    is_single = serializers.BooleanField()

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class PollAnswerOut(serializers.Serializer):
    title = serializers.CharField()
    questions = serializers.ListField(child=QuestionAnswer())

    def create(self, validated_data):
        pass

    def update(self, instance, validated_data):
        pass


class ChangeShareStatusIn(serializers.ModelSerializer):
    id = serializers.IntegerField(help_text='poll ID')

    class Meta:
        model = Poll
        fields = ('id', 'share')
