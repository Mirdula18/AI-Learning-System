from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class LearnerProfile(models.Model):
    LEARNING_GOALS = [
        ('career_switch', 'Career Switch to Tech'),
        ('upskill', 'Upskill for Current Job'),
        ('personal_project', 'Build Personal Projects'),
        ('academic', 'Supplement Academic Studies'),
        ('freelance', 'Start Freelancing'),
        ('explore', 'Just Exploring'),
    ]
    
    PREFERRED_TIMES = [
        ('early_morning', 'Early Morning (6-9 AM)'),
        ('evening', 'Evening (6-10 PM)'),
        ('weekend', 'Weekends'),
        ('flexible', 'Flexible'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    learning_goal = models.CharField(max_length=50, choices=LEARNING_GOALS)
    weekly_hours = models.IntegerField(default=6)
    preferred_time = models.CharField(max_length=20, choices=PREFERRED_TIMES)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} Profile"


class Course(models.Model):
    course_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon_emoji = models.CharField(max_length=10, default='📚')
    difficulty_range = models.CharField(max_length=50)
    estimated_weeks_min = models.IntegerField(default=6)
    estimated_weeks_max = models.IntegerField(default=8)
    topics_covered = models.JSONField(default=list)
    prerequisites = models.JSONField(default=list)
    learning_outcomes = models.JSONField(default=list)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title


class Assessment(models.Model):
    STATUS_CHOICES = [
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)  # Optional for custom courses
    quiz_data = models.JSONField()
    user_answers = models.JSONField(default=dict, blank=True)
    evaluation_results = models.JSONField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    custom_course_name = models.CharField(max_length=200, null=True, blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        course_name = self.custom_course_name or (self.course.title if self.course else 'Unknown')
        return f"{self.user.username} - {course_name}"


class SkillProfile(models.Model):
    SKILL_LEVELS = [
        ('absolute_beginner', 'Absolute Beginner'),
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    LEARNING_PACE = [
        ('slow', 'Slow'),
        ('moderate', 'Moderate'),
        ('fast', 'Fast'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, null=True, blank=True)
    assessment = models.OneToOneField(Assessment, on_delete=models.CASCADE)
    skill_level = models.CharField(max_length=20, choices=SKILL_LEVELS)
    confidence_score = models.IntegerField()
    learning_pace = models.CharField(max_length=20, choices=LEARNING_PACE)
    strengths = models.JSONField(default=list)
    weaknesses = models.JSONField(default=list)
    estimated_weeks = models.IntegerField()
    raw_results = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"{self.user.username} - {self.skill_level}"
