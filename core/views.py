from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from django.db import models
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework import status
from .models import (
    LearnerProfile, Course, Assessment, SkillProfile,
    TopicResource, Assignment, AssignmentSubmission
)
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
        
        # ⭐ AUTOMATIC RESOURCE GENERATION ⭐
        # Generate learning resources for all topics in the roadmap
        try:
            from .resource_generator import generate_resources_for_roadmap
            
            logger.info(f"Starting automatic resource generation for roadmap topics...")
            resource_stats = generate_resources_for_roadmap(roadmap_data, skill_level)
            
            logger.info(f"Resource generation complete: {resource_stats}")
            
            # Add resource stats to roadmap data
            roadmap_data['resource_generation_stats'] = resource_stats
            
        except Exception as resource_error:
            # Don't fail the entire roadmap if resource generation fails
            logger.error(f"Resource generation failed: {str(resource_error)}")
            roadmap_data['resource_generation_stats'] = {
                'error': 'Resource generation failed',
                'message': str(resource_error)
            }
        
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


# ==================== ROADMAP & ASSIGNMENT TRACKING VIEWS ====================

def roadmap_page(request):
    """Display personalized learning roadmap"""
    return render(request, 'roadmap.html')


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def topic_detail_api(request):
    """
    Get topic details with resources and assignments
    Filters out completed assignments for the current user
    """
    try:
        from .models import TopicResource, Assignment, AssignmentSubmission
        
        topic_name = request.query_params.get('topic')
        
        if not topic_name:
            return Response(
                {'error': 'Topic name required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get resources for this topic
        resources = TopicResource.objects.filter(topic=topic_name)
        
        # Get all assignments for this topic
        all_assignments = Assignment.objects.filter(topic=topic_name)
        
        # Filter out completed assignments for this user
        completed_assignment_ids = AssignmentSubmission.objects.filter(
            user=request.user,
            status='completed'
        ).values_list('assignment_id', flat=True)
        
        # Only show assignments that are not completed
        pending_assignments = all_assignments.exclude(id__in=completed_assignment_ids)
        
        # Serialize data
        resources_data = TopicResourceSerializer(resources, many=True).data
        assignments_data = AssignmentSerializer(
            pending_assignments,
            many=True,
            context={'request': request}
        ).data
        
        # Calculate completion stats
        total_assignments = all_assignments.count()
        completed_count = len(completed_assignment_ids)
        completion_percentage = (completed_count / total_assignments * 100) if total_assignments > 0 else 0
        
        response_data = {
            'topic_name': topic_name,
            'resources': resources_data,
            'assignments': assignments_data,
            'completion_stats': {
                'total': total_assignments,
                'completed': completed_count,
                'pending': total_assignments - completed_count,
                'percentage': round(completion_percentage, 2)
            }
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Topic detail error: {str(e)}")
        return Response(
            {'error': 'Failed to retrieve topic details'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_assignments_api(request):
    """
    Get all assignments for the current user with their submission status
    Excludes completed assignments by default
    """
    try:
        from .models import Assignment, AssignmentSubmission
        
        include_completed = request.query_params.get('include_completed', 'false').lower() == 'true'
        
        # Get all assignments
        all_assignments = Assignment.objects.all()
        
        if not include_completed:
            # Filter out completed assignments
            completed_assignment_ids = AssignmentSubmission.objects.filter(
                user=request.user,
                status='completed'
            ).values_list('assignment_id', flat=True)
            
            assignments = all_assignments.exclude(id__in=completed_assignment_ids)
        else:
            assignments = all_assignments
        
        # Serialize with user submission status
        serializer = AssignmentSerializer(
            assignments,
            many=True,
            context={'request': request}
        )
        
        return Response({
            'assignments': serializer.data,
            'total_count': assignments.count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"User assignments error: {str(e)}")
        return Response(
            {'error': 'Failed to retrieve assignments'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_assignment_api(request):
    """
    Submit an assignment
    Creates or updates AssignmentSubmission record
    """
    try:
        from .models import Assignment, AssignmentSubmission
        
        assignment_id = request.data.get('assignment_id')
        submission_text = request.data.get('submission_text', '').strip()
        submission_link = request.data.get('submission_link', '').strip()
        
        if not assignment_id:
            return Response(
                {'error': 'Assignment ID required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate at least one submission method
        if not submission_text and not submission_link:
            return Response(
                {'error': 'Please provide either submission text or a link'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get assignment
        try:
            assignment = Assignment.objects.get(id=assignment_id)
        except Assignment.DoesNotExist:
            return Response(
                {'error': 'Assignment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create or update submission
        submission, created = AssignmentSubmission.objects.update_or_create(
            user=request.user,
            assignment=assignment,
            defaults={
                'submission_text': submission_text,
                'submission_link': submission_link,
                'status': 'submitted',
                'submitted_at': timezone.now()
            }
        )
        
        logger.info(f"Assignment {assignment_id} submitted by user {request.user.id}")
        
        serializer = AssignmentSubmissionSerializer(submission)
        
        return Response({
            'message': 'Assignment submitted successfully',
            'submission': serializer.data
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"Assignment submission error: {str(e)}")
        return Response(
            {'error': 'Failed to submit assignment'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_progress_api(request):
    """
    Get overall user progress across all assignments
    Returns statistics and recent submissions
    """
    try:
        from .models import Assignment, AssignmentSubmission
        
        user = request.user
        
        # Get all assignments
        total_assignments = Assignment.objects.count()
        
        # Get user submissions
        user_submissions = AssignmentSubmission.objects.filter(user=user)
        
        # Calculate stats
        completed_count = user_submissions.filter(status='completed').count()
        submitted_count = user_submissions.filter(status='submitted').count()
        graded_count = user_submissions.filter(status='graded').count()
        
        # Calculate total score
        total_score = user_submissions.filter(
            score__isnull=False
        ).aggregate(total=models.Sum('score'))['total'] or 0
        
        # Get recent submissions
        recent_submissions = user_submissions.order_by('-updated_at')[:5]
        recent_data = AssignmentSubmissionSerializer(recent_submissions, many=True).data
        
        # Calculate completion percentage
        completion_percentage = (completed_count / total_assignments * 100) if total_assignments > 0 else 0
        
        # Get total time spent
        total_time_spent = user.profile.total_time_spent if hasattr(user, 'profile') else 0
        
        return Response({
            'total_assignments': total_assignments,
            'completed': completed_count,
            'submitted': submitted_count,
            'graded': graded_count,
            'pending': total_assignments - completed_count - submitted_count - graded_count,
            'completion_percentage': round(completion_percentage, 2),
            'total_score': total_score,
            'total_time_spent': total_time_spent,
            'recent_submissions': recent_data
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        logger.error(f"User progress error: {str(e)}")
        return Response(
            {'error': 'Failed to retrieve progress'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_learning_time(request):
    """
    Update user's total learning time
    Expects 'increment' in body (minutes), defaults to 1
    """
    try:
        user = request.user
        profile = hasattr(user, 'profile') and user.profile or None
        
        if not profile:
            # Create profile if it doesn't exist (fallback)
            profile = LearnerProfile.objects.create(
                user=user,
                learning_goal='explore',
                preferred_time='flexible'
            )
        
        increment = int(request.data.get('increment', 1))
        
        # Ensure increment is reasonable (e.g., <= 60 minutes per call)
        if increment > 60:
            increment = 60
        if increment < 0:
            increment = 0
            
        profile.total_time_spent += increment
        profile.save()
        
        return Response({
            'status': 'success',
            'total_time_spent': profile.total_time_spent,
            'message': f'Added {increment} minutes'
        })
        
    except ValueError:
        return Response(
            {'error': 'Invalid increment value'},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        logger.error(f"Error updating time: {str(e)}")
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
