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

def results_page(request, assessment_id=None):
    """Display assessment results page"""
    context = {
        'assessment_id': assessment_id
    }
    return render(request, 'results.html', context)


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
    """Generate and start assessment for custom course typed by user"""
    try:
        user = request.user
        course_name = request.data.get('course_name', '').strip()
        
        logger.info(f"Starting custom assessment for: {course_name}")
        
        # Validate course name
        if not course_name or len(course_name) < 2:
            return Response(
                {'error': 'Course name must be at least 2 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(course_name) > 100:
            return Response(
                {'error': 'Course name too long (max 100 characters)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Import here to avoid circular imports
        from .quiz_generator import generate_assessment_quiz
        
        # Generate dynamic quiz for the custom course
        quiz_data = generate_assessment_quiz(course_name, user)
        
        if not quiz_data:
            logger.error(f"Failed to generate quiz for course: {course_name}")
            return Response(
                {'error': 'Failed to generate assessment. Please try again or use a different topic.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        logger.info(f"Quiz generated with {len(quiz_data.get('questions', []))} questions")
        
        # Create assessment record
        assessment = Assessment.objects.create(
            user=user,
            course=None,  # No associated course since it's custom
            quiz_data=quiz_data,
            status='in_progress',
            started_at=timezone.now()
        )
        
        # Store custom course name for reference
        assessment.custom_course_name = course_name
        assessment.save()
        
        logger.info(f"Assessment {assessment.id} created for {course_name}")
        
        # Prepare quiz for frontend (hide correct answers)
        quiz_for_display = {
            'assessment_id': assessment.id,
            'course_name': course_name,
            'metadata': quiz_data.get('quiz_metadata', {}),
            'questions': [
                {
                    'question_id': q['question_id'],
                    'question_number': q['question_number'],
                    'difficulty': q['difficulty'],
                    'topic': q['topic'],
                    'question_text': q['question_text'],
                    'code_snippet': q.get('code_snippet', ''),
                    'options': q['options']
                }
                for q in quiz_data.get('questions', [])
            ]
        }
        
        logger.info(f"Assessment response prepared with {len(quiz_for_display['questions'])} questions")
        
        return Response({
            'message': 'Assessment generated successfully',
            'quiz': quiz_for_display,
            'assessment_id': assessment.id
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Error in start_custom_assessment: {str(e)}", exc_info=True)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_assessment(request):
    """Submit assessment answers and get evaluation"""
    try:
        user = request.user
        assessment_id = request.data.get('assessment_id')
        user_answers = request.data.get('user_answers', {})
        time_taken = request.data.get('time_taken', 0)
        
        # Get assessment
        assessment = Assessment.objects.get(id=assessment_id, user=user)
        
        # Store user answers
        assessment.user_answers = user_answers
        assessment.save()
        
        # Evaluate assessment
        from .evaluator import evaluate_assessment
        evaluation_results = evaluate_assessment(assessment, user_answers, time_taken)
        
        if not evaluation_results:
            return Response(
                {'error': 'Failed to evaluate assessment'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Store evaluation results
        assessment.evaluation_results = evaluation_results
        assessment.status = 'completed'
        assessment.completed_at = timezone.now()
        assessment.save()
        
        logger.info(f"Assessment {assessment_id} submitted by user {user.id}")
        
        return Response({
            'message': 'Assessment evaluated successfully',
            'assessment_id': assessment.id,
            'evaluation_results': evaluation_results,
            'learner_profile': evaluation_results.get('learner_profile', {}),
            'overall_score': evaluation_results.get('overall_score', 0)
        }, status=status.HTTP_200_OK)
        
    except Assessment.DoesNotExist:
        return Response(
            {'error': 'Assessment not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Assessment submission error: {str(e)}")
        return Response(
            {'error': 'An error occurred'},
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
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_roadmap(request):
    """Generate personalized learning roadmap based on assessment"""
    try:
        user = request.user
        assessment_id = request.data.get('assessment_id')
        
        if not assessment_id:
            return Response(
                {'error': 'Assessment ID required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get assessment
        assessment = Assessment.objects.get(id=assessment_id, user=user)
        
        if not assessment.evaluation_results:
            return Response(
                {'error': 'Assessment not yet evaluated'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Extract data for roadmap generation
        eval_results = assessment.evaluation_results
        learner_profile = eval_results.get('learner_profile', {})
        topic = assessment.custom_course_name or (assessment.course.title if assessment.course else 'General')
        
        skill_level = learner_profile.get('skill_level', 'beginner')
        weaknesses = learner_profile.get('weaknesses', [])
        strengths = learner_profile.get('strengths', [])
        weekly_hours = user.profile.weekly_hours if hasattr(user, 'profile') else 5
        
        # Import here to avoid circular imports
        from .roadmap_generator import generate_learning_roadmap
        
        # Generate roadmap
        roadmap_data = generate_learning_roadmap(
            topic=topic,
            skill_level=skill_level,
            weaknesses=weaknesses,
            strengths=strengths,
            weekly_hours=weekly_hours
        )
        
        if not roadmap_data:
            return Response(
                {'error': 'Failed to generate roadmap'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Store roadmap (optional - for future reference)
        assessment.roadmap_data = roadmap_data
        assessment.save()
        
        logger.info(f"Roadmap generated for user {user.id} - Topic: {topic}")
        
        return Response({
            'message': 'Roadmap generated successfully',
            'roadmap': roadmap_data
        }, status=status.HTTP_200_OK)
        
    except Assessment.DoesNotExist:
        return Response(
            {'error': 'Assessment not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        logger.error(f"Error in generate_roadmap: {str(e)}")
        return Response(
            {'error': 'An error occurred'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

