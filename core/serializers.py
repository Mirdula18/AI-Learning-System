from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    LearnerProfile, Course, Assessment, SkillProfile,
    TopicResource, Assignment, AssignmentSubmission
)

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class LearnerProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = LearnerProfile
        fields = '__all__'


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = '__all__'


class AssessmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assessment
        fields = '__all__'


class SkillProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillProfile
        fields = '__all__'


class TopicResourceSerializer(serializers.ModelSerializer):
    """
    Serializer for learning resources (documents, videos, articles)
    """
    class Meta:
        model = TopicResource
        fields = ['id', 'topic', 'title', 'description', 'resource_type', 'url', 'order', 'created_at']


class AssignmentSubmissionSerializer(serializers.ModelSerializer):
    """
    Serializer for assignment submissions
    """
    assignment_title = serializers.CharField(source='assignment.title', read_only=True)
    assignment_topic = serializers.CharField(source='assignment.topic', read_only=True)
    
    class Meta:
        model = AssignmentSubmission
        fields = [
            'id', 'user', 'assignment', 'assignment_title', 'assignment_topic',
            'status', 'submission_text', 'submission_link', 'score', 'feedback',
            'submitted_at', 'graded_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'score', 'feedback', 'graded_at']


class AssignmentSerializer(serializers.ModelSerializer):
    """
    Serializer for assignments with user-specific submission status
    """
    user_submission = serializers.SerializerMethodField()
    
    class Meta:
        model = Assignment
        fields = [
            'id', 'topic', 'title', 'description', 'instructions',
            'difficulty', 'estimated_hours', 'total_points', 'created_at',
            'user_submission'
        ]
    
    def get_user_submission(self, obj):
        """
        Get the current user's submission status for this assignment
        Returns None if no submission exists
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                submission = AssignmentSubmission.objects.get(
                    user=request.user,
                    assignment=obj
                )
                return {
                    'id': submission.id,
                    'status': submission.status,
                    'score': submission.score,
                    'submitted_at': submission.submitted_at,
                }
            except AssignmentSubmission.DoesNotExist:
                return None
        return None


class TopicDetailSerializer(serializers.Serializer):
    """
    Enhanced serializer for topic details with resources and assignments
    """
    topic_name = serializers.CharField()
    resources = TopicResourceSerializer(many=True)
    assignments = AssignmentSerializer(many=True)
    completion_stats = serializers.DictField()

