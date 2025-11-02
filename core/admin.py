from django.contrib import admin
from .models import LearnerProfile, Course, Assessment, SkillProfile

@admin.register(LearnerProfile)
class LearnerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'learning_goal', 'weekly_hours', 'created_at']
    list_filter = ['learning_goal', 'preferred_time']
    search_fields = ['user__username', 'user__email']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'course_id', 'difficulty_range', 'is_available']
    list_filter = ['is_available']
    search_fields = ['title', 'course_id']


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'status', 'score', 'started_at']
    list_filter = ['status', 'course']
    search_fields = ['user__username']


@admin.register(SkillProfile)
class SkillProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'skill_level', 'confidence_score', 'created_at']
    list_filter = ['skill_level', 'learning_pace']
    search_fields = ['user__username']
