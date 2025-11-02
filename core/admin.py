from django.contrib import admin
from .models import LearnerProfile, Course, Assessment, SkillProfile

@admin.register(LearnerProfile)
class LearnerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'learning_goal', 'weekly_hours']
    search_fields = ['user__username']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'difficulty_range', 'course_id']
    search_fields = ['title']

@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'status', 'started_at']
    search_fields = ['user__username']
    readonly_fields = ['quiz_data', 'user_answers', 'evaluation_results']

@admin.register(SkillProfile)
class SkillProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'skill_level']
    search_fields = ['user__username']
