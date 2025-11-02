from rest_framework import serializers
from django.contrib.auth.models import User
from .models import LearnerProfile, Course, Assessment, SkillProfile

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
