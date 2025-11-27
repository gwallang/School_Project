from django.contrib import admin
from .models import CustomUser, Exam, Question, Attempt, StudentAnswer,Subject,StudyMaterial, Topic
from django.contrib.auth.admin import UserAdmin


admin.site.register(CustomUser)
# admin.site.register(Studymaterial)
admin.site.register(Exam)
admin.site.register(Subject)
admin.site.register(Question)
admin.site.register(Attempt)
admin.site.register(StudentAnswer)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'topic', 'uploaded_by', 'uploaded_at')
    search_fields = ('title', 'uploaded_by__username')
    list_filter = ('topic', 'uploaded_at')
