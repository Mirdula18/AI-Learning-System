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
    path('results/<int:assessment_id>/', views.results_page, name='results'),
    
    # API endpoints
    path('api/auth/register/', views.register_user, name='api_register'),
    path('api/auth/login/', views.login_user, name='api_login'),
    path('api/profile/create/', views.create_profile, name='api_create_profile'),
    path('api/courses/', views.get_courses, name='api_courses'),
    path('api/assessment/start/', views.start_assessment, name='api_start_assessment'),
    path('api/assessment/submit/', views.submit_assessment, name='api_submit_assessment'),
    path('api/assessment/<int:assessment_id>/results/', views.get_results, name='api_results'),
]
