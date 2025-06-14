# users/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('signup/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    path('onboarding/', views.create_career_profile, name='career_profile_onboarding'),


    path("access-log-dashboard/", views.access_log_dashboard, name="access_log_dashboard"),
]
