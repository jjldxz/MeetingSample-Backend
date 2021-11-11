from django.contrib import admin
from safedelete.admin import SafeDeleteAdmin

# Register your models here.
from poll.models import Poll, PollQuestion, PollOption, PollResult


@admin.register(Poll)
class PollAdmin(SafeDeleteAdmin):
    list_display = ('id', 'meeting', 'title', 'status', 'is_anonymous', 'deleted', 'share')
    readonly_fields = ('id',)


@admin.register(PollQuestion)
class PollQuestionAdmin(SafeDeleteAdmin):
    list_display = ('id', 'poll', 'content', 'is_single', 'deleted')
    readonly_fields = ('id',)


@admin.register(PollOption)
class PollOptionAdmin(SafeDeleteAdmin):
    list_display = ('id', 'question', 'content', 'deleted')
    readonly_fields = ('id',)


@admin.register(PollResult)
class PollResultAdmin(SafeDeleteAdmin):
    list_display = ('id', 'poll', 'question', 'option', 'deleted', 'voter')
    readonly_fields = ('id',)

    def voter(self, obj):
        return [x.nickname for x in obj.voters.all()]
