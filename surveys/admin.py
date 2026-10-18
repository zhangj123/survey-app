from django.contrib import admin

from .models import Answer, Question, Response, Survey


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 0


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ("title", "owner", "is_published", "estimated_minutes", "created_at")
    list_filter = ("is_published",)
    inlines = [QuestionInline]


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ("survey", "user", "submitted_at")


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ("response", "question")
