from django.contrib.auth.models import User
from django.db import models
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel

# Create your models here.
from meeting.models import Meeting


class Poll(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    class Status(models.IntegerChoices):
        NEW = 0
        ONGOING = 1
        DONE = 2

    class ShareStatus(models.Choices):
        STOP = False
        START = True

    meeting = models.ForeignKey(Meeting, on_delete=models.CASCADE, null=True)
    title = models.CharField(max_length=200)
    round = models.IntegerField(help_text='how many times do this poll', default=0)
    status = models.IntegerField(choices=Status.choices, default=Status.NEW.value)
    is_anonymous = models.BooleanField(default=True)
    share = models.BooleanField(choices=ShareStatus.choices, default=ShareStatus.STOP.value)

    class Meta:
        db_table = 'poll'

    def __str__(self):
        return self.title


class PollQuestion(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    poll = models.ForeignKey(Poll, on_delete=models.CASCADE)
    content = models.TextField()
    is_single = models.BooleanField(default=True)

    class Meta:
        db_table = 'poll_question'

    def __str__(self):
        return self.content


class PollOption(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    question = models.ForeignKey(PollQuestion, on_delete=models.CASCADE)
    content = models.TextField()

    class Meta:
        db_table = 'poll_option'

    def __str__(self):
        return self.content


class PollResult(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, null=True)
    question = models.ForeignKey(PollQuestion, on_delete=models.CASCADE, null=True)
    option = models.ForeignKey(PollOption, on_delete=models.CASCADE, null=True)
    round = models.IntegerField(default=0)
    voter = models.ForeignKey(User, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = 'poll_result'
