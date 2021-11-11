import datetime

from django.contrib.auth.models import User
from django.db import models
from safedelete import SOFT_DELETE_CASCADE
from safedelete.models import SafeDeleteModel


# Create your models here.
class Meeting(SafeDeleteModel):
    _safedelete_policy = SOFT_DELETE_CASCADE

    class RoomStatus(models.IntegerChoices):
        NEW = 0
        ONGOING = 1
        CLOSED = 2

    class MuteType(models.IntegerChoices):
        UNMUTE = 0
        ALL_MUTE = 1
        AUTO = 2

    name = models.CharField(max_length=128)
    status = models.IntegerField(choices=RoomStatus.choices, default=RoomStatus.NEW)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owner_user')
    call_number = models.IntegerField(primary_key=True)
    created = models.DateTimeField()

    begin_at = models.DateTimeField()
    end_at = models.DateTimeField()
    mute_type = models.IntegerField(choices=MuteType.choices, default=0)

    actually_begin_at = models.DateTimeField(null=True, blank=True)
    actually_end_at = models.DateTimeField(null=True, blank=True)
    closed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name='close_user')

    password = models.CharField(max_length=512, null=True, blank=True)
    share_user_id = models.IntegerField(null=True)

    class Meta:
        db_table = 'meeting'
        ordering = ('-created',)

    def __str__(self):
        return str(self.call_number)
