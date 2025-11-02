from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from .models import LearnerProfile, Course, Assessment, SkillProfile
from .serializers import *
from .quiz_generator import generate_assessment_quiz
from .evaluator import evaluate_assessment
import logging

logger = logging.getLogger(__name__)

# Template views
def index(request):
    return render(request, 'index.html')

def register_page(request):
    return render(request, 'register.html')

def login_page(request):
    return render(request, 'login.html')

def profile_page(request):
    return render(request, 'profile.html')

def courses_page(request):
    return render(request, 'courses.html')

def assessment_page(request):
    return render(request, 'assessment.html')

def results_page(request, assessment_id):
    return render(request, 'results.html', {'assessment_id': assessment_id})


# API endpoints
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    """Register new user"""
    try:
        full_name = request.data.get('full_name')
        email = request.data.get('email')
        password = request.data.get('password')
        
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Email already registered'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        name_parts = full_name.split()
        first_name = name_parts[0]
        last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
        
        user = User.objects.create(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
            password=make_password(password)
        )
        
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.id,
            'message': 'Account created successfully'
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return Response(
            {'error': 'Registration failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_user(request):
    """Login user"""
    try:
        from django.contrib.auth import authenticate
        
        email = request.data.get('email')
        password = request.data.get('password')
        
        user = authenticate(username=email, password=password)
        
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user_id': user.id,
                'message': 'Login successful'
            })
        else:
            return Response(
                {'error': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return Response(
            {'error': 'Login failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_profile(request):
    """Create learner profile"""
    try:
        user = request.user
        
        profile, created = LearnerProfile.objects.update_or_create(
            user=user,
            defaults={
                'learning_goal': request.data.get('learning_goal'),
                'weekly_hours': request.data.get('weekly_hours'),
                'preferred_time': request.data.get('preferred_time')
            }
        )
        
        return Response({
            'message': 'Profile created successfully',
            'profile_id': profile.id
        })
        
    except Exception as e:
        logger.error(f"Profile creation error: {str(e)}")
        return Response(
            {'error': 'Profile creation failed'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_courses(request):
    """Get available courses"""
    try:
        courses = Course.objects.filter(is_available=True)
        serializer = CourseSerializer(courses, many=True)
        return Response(serializer.data)
        
    except Exception as e:
        logger.error(f"Course retrieval error: {str(e)}")
        return Response(
            {'error': 'Failed to retrieve courses'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_assessment(request):
    """Generate and start assessment"""
    try:
        user = request.user
        course_id = request.data.get('course_id')
        
        course = Course.objects.get(course_id=course_id)
        
        # Generate quiz
        quiz_data = generate_assessment_quiz(course, user)
        
        if not quiz_data:
            return Response(
                {'error': 'Failed to generate quiz'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Create assessment
        assessment = Assessment.objects.create(
            user=user,
            course=course,
            quiz_data=quiz_data,
            status='in_progress',
            started_at=timezone.now()
        )
        
        # Prepare quiz for frontend (hide answers)
        quiz_for_display = {
            'assessment_id': assessment.id,
            'metadata': quiz_data['quiz_metadata'],
            'questions': [
                {
                    'question_id': q['question_id'],
                    'question_number': q['question_number'],
                    'difficulty': q['difficulty'],
                    'topic': q['topic'],
                    'question_text': q['question_text'],
                    'code_snippet': q.get('code_snippet'),
                    'options': q['options']
                }
                for q in quiz_data['questions']
            ]
        }
        
        return Response({
            'message': 'Assessment generated successfully',
            'quiz': quiz_for_display
        })
        
    except Course.DoesNotExist:
        return Response(
            {'error': 'Course not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Assessment start error: {str(e)}")
        return Response(
            {'error': 'Failed to start assessment'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_assessment(request):
    """Submit and evaluate assessment"""
    try:
        assessment_id = request.data['assessment_id']
        user_answers = request.data['answers']
        time_taken = request.data['total_time_seconds']
        
        assessment = Assessment.objects.get(id=assessment_id, user=request.user)
        
        # Evaluate
        results = evaluate_assessment(assessment, user_answers, time_taken)
        
        # Update assessment
        assessment.status = 'completed'
        assessment.user_answers = user_answers
        assessment.score = results['overall_score']
        assessment.submitted_at = timezone.now()
        assessment.time_taken_seconds = time_taken
        assessment.save()
        
        # Create skill profile
        skill_profile = SkillProfile.objects.create(
            user=request.user,
            course=assessment.course,
            assessment=assessment,
            skill_level=results['learner_profile']['skill_level'],
            confidence_score=results['learner_profile']['confidence_score'],
            learning_pace=results['learner_profile']['learning_pace'],
            strengths=results['learner_profile']['strengths'],
            weaknesses=results['learner_profile']['weaknesses'],
            estimated_weeks=results['learner_profile']['estimated_weeks_to_proficiency'],
            raw_results=results
        )
        
        return Response({
            'message': 'Assessment evaluated successfully',
            'assessment_id': assessment_id,
            'results_url': f'/results/{assessment_id}/'
        })
        
    except Assessment.DoesNotExist:
        return Response(
            {'error': 'Assessment not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Assessment submission error: {str(e)}")
        return Response(
            {'error': 'Failed to submit assessment'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_results(request, assessment_id):
    """Get assessment results"""
    try:
        assessment = Assessment.objects.get(id=assessment_id, user=request.user)
        skill_profile = SkillProfile.objects.get(assessment=assessment)
        
        return Response({
            'assessment_id': assessment.id,
            'evaluation_results': skill_profile.raw_results,
            'learner_profile': {
                'skill_level': skill_profile.skill_level,
                'confidence_score': skill_profile.confidence_score,
                'learning_pace': skill_profile.learning_pace,
                'strengths': skill_profile.strengths,
                'weaknesses': skill_profile.weaknesses,
                'estimated_weeks_to_proficiency': skill_profile.estimated_weeks,
                'personalized_message': skill_profile.raw_results['learner_profile']['personalized_message'],
                'next_steps': skill_profile.raw_results['learner_profile']['next_steps']
            }
        })
        
    except Assessment.DoesNotExist:
        return Response(
            {'error': 'Assessment not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except SkillProfile.DoesNotExist:
        return Response(
            {'error': 'Results not available yet'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Results retrieval error: {str(e)}")
        return Response(
            {'error': 'Failed to retrieve results'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
