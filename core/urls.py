from django.urls import path
from . import views

urlpatterns = [
    # Template views
    path('', views.index, name='index'),
    path('register/', views.register_page, name='register'),
    path('login/', views.login_page, name='login'),
    path('profile/', views.profile_page, name='profile'),
    path('courses/', views.courses_page, name='courses'),
    path('assessment/', views.assessment_page, name='assessment'),
    path('results/', views.results_page, name='results_page_simple'),
    path('results/<int:assessment_id>/', views.results_page, name='results'),
    
    # API endpoints
    path('api/auth/register/', views.register_user, name='api_register'),
    path('api/auth/login/', views.login_user, name='api_login'),
    path('api/profile/', views.get_profile, name='api_get_profile'),
    path('api/profile/create/', views.create_profile, name='api_create_profile'),
    path('api/courses/', views.get_courses, name='api_courses'),
    path('api/assessment/start/', views.start_assessment, name='api_start_assessment'),
    path('api/assessment/submit/', views.submit_assessment, name='api_submit_assessment'),
    path('api/assessment/<int:assessment_id>/results/', views.get_results, name='api_results'),
    path('api/assessment/start-custom/', views.start_assessment, name='api_start_assessment'),
    path('api/roadmap/generate/', views.generate_roadmap, name='api_generate_roadmap'),
    
    # Roadmap & Assignment tracking
    path('roadmap/', views.roadmap_page, name='roadmap'),
    path('api/roadmap/topic-detail/', views.topic_detail_api, name='api_topic_detail'),
    path('api/assignments/user/', views.user_assignments_api, name='api_user_assignments'),
    path('api/assignments/submit/', views.submit_assignment_api, name='api_submit_assignment'),
    path('api/assignments/progress/', views.user_progress_api, name='api_user_progress'),
    path('api/profile/update-time/', views.update_learning_time, name='api_update_time'),
    path('api/roadmaps/user/', views.get_user_roadmaps, name='api_user_roadmaps'),
    path('api/roadmaps/<int:assessment_id>/', views.get_roadmap_details, name='api_roadmap_details'),

]
