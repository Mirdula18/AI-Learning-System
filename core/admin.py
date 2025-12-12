from django.contrib import admin
from .models import (
    LearnerProfile, Course, Assessment, SkillProfile,
    TopicResource, Assignment, AssignmentSubmission
)

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


@admin.register(TopicResource)
class TopicResourceAdmin(admin.ModelAdmin):
    list_display = ['topic', 'title', 'resource_type', 'order', 'created_at']
    list_filter = ['resource_type', 'topic']
    search_fields = ['topic', 'title', 'description']
    ordering = ['topic', 'order']
    list_editable = ['order']


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['topic', 'title', 'difficulty', 'estimated_hours', 'total_points', 'created_at']
    list_filter = ['difficulty', 'topic']
    search_fields = ['topic', 'title', 'description']
    ordering = ['topic', 'difficulty']
    fieldsets = (
        ('Basic Information', {
            'fields': ('topic', 'title', 'description')
        }),
        ('Assignment Details', {
            'fields': ('instructions', 'difficulty', 'estimated_hours', 'total_points')
        }),
    )


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'assignment_title', 'assignment_topic', 'status', 'score', 'submitted_at', 'graded_at']
    list_filter = ['status', 'assignment__topic', 'submitted_at', 'graded_at']
    search_fields = ['user__username', 'assignment__title', 'assignment__topic']
    readonly_fields = ['user', 'assignment', 'submission_text', 'submission_link', 'submitted_at', 'created_at', 'updated_at']
    ordering = ['-updated_at']
    
    fieldsets = (
        ('Submission Information', {
            'fields': ('user', 'assignment', 'status', 'submitted_at')
        }),
        ('Student Work', {
            'fields': ('submission_text', 'submission_link')
        }),
        ('Grading', {
            'fields': ('score', 'feedback', 'graded_at'),
            'description': 'Use this section to grade and provide feedback'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def assignment_title(self, obj):
        return obj.assignment.title
    assignment_title.short_description = 'Assignment'
    
    def assignment_topic(self, obj):
        return obj.assignment.topic
    assignment_topic.short_description = 'Topic'
    
    actions = ['mark_as_completed']
    
    def mark_as_completed(self, request, queryset):
        """Bulk action to mark submissions as completed"""
        updated = queryset.update(status='completed')
        self.message_user(request, f'{updated} submission(s) marked as completed.')
    mark_as_completed.short_description = 'Mark selected submissions as completed'

