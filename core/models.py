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
    total_time_spent = models.IntegerField(default=0, help_text="Total time spent learning in minutes")
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


class TopicResource(models.Model):
    """
    Store learning resources for each topic in the roadmap
    (documents, videos, articles, external links)
    """
    RESOURCE_TYPES = [
        ('document', 'Document'),
        ('video', 'Video'),
        ('article', 'Article'),
        ('link', 'External Link'),
    ]
    
    topic = models.CharField(max_length=200, help_text="Topic name from roadmap")
    title = models.CharField(max_length=300)
    description = models.TextField(blank=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPES)
    url = models.URLField(max_length=500)
    order = models.IntegerField(default=0, help_text="Display order within topic")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['topic', 'order', 'created_at']
    
    def __str__(self):
        return f"{self.topic} - {self.title}"


class Assignment(models.Model):
    """
    Define assignments for each topic
    """
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    topic = models.CharField(max_length=200, help_text="Topic name from roadmap")
    title = models.CharField(max_length=300)
    description = models.TextField()
    instructions = models.TextField(help_text="Detailed assignment instructions")
    difficulty = models.CharField(max_length=10, choices=DIFFICULTY_CHOICES, default='medium')
    estimated_hours = models.IntegerField(default=2, help_text="Estimated time to complete")
    total_points = models.IntegerField(default=100, help_text="Maximum points for this assignment")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['topic', 'difficulty', 'created_at']
    
    def __str__(self):
        return f"{self.topic} - {self.title} ({self.difficulty})"


class AssignmentSubmission(models.Model):
    """
    Track user-specific assignment submissions and completion status
    CRITICAL: Persists across login/logout to hide completed assignments
    """
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('pending', 'Pending'),
        ('submitted', 'Submitted'),
        ('graded', 'Graded'),
        ('completed', 'Completed'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assignment_submissions')
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    submission_text = models.TextField(blank=True, help_text="Text submission or answer")
    submission_link = models.URLField(max_length=500, blank=True, help_text="Link to submission (GitHub, etc.)")
    score = models.IntegerField(null=True, blank=True, help_text="Points earned")
    feedback = models.TextField(blank=True, help_text="Instructor feedback")
    submitted_at = models.DateTimeField(null=True, blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'assignment']  # One submission per user per assignment
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.assignment.title} ({self.status})"
    
    def mark_as_submitted(self):
        """Mark submission as submitted with timestamp"""
        self.status = 'submitted'
        self.submitted_at = timezone.now()
        self.save()
    
    def mark_as_completed(self):
        """Mark submission as completed (used after grading)"""
        self.status = 'completed'
        self.graded_at = timezone.now()
        self.save()
