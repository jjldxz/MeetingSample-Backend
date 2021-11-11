from django.contrib import admin
from safedelete.admin import SafeDeleteAdmin

from meeting.models import Meeting


@admin.register(Meeting)
class RoomAdmin(SafeDeleteAdmin):
    list_display = (
        'call_number', 'name', 'created', 'begin_at', 'end_at', 'status', 'owner', 'mute_type',
        'actually_begin_at', 'actually_end_at', 'closed_by', 'deleted')

    search_fields = ('call_number',)
    readonly_fields = ('call_number',)
