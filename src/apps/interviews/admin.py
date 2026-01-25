from django.contrib import admin
from .models import Question, InterviewSession, InterviewTurn

@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('topic', 'difficulty', 'text')
    list_filter = ('difficulty', 'topic')

@admin.register(InterviewSession)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'status', 'start_time', 'total_score')

@admin.register(InterviewTurn)
class TurnAdmin(admin.ModelAdmin):
    list_display = ('session', 'question', 'score', 'created_at')