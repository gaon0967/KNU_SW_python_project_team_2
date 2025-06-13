# main/urls.py

from django.urls import path

from . import views

urlpatterns = [ 
    path('', views.rehome, name='home'),
    path('dashboard_1/', views.dashboard_1, name='dashboard_1'),
    path('dashboard_2/', views.dashboard_2, name='dashboard_2'),
    path('dashboard_3/', views.dashboard_3, name='dashboard_3'),
    path('dashboard_4/', views.dashboard_4, name='dashboard_4'),
    path('how-to-use/', views.how_to_use, name='how_to_use'),
    path('emergency-contacts/', views.emergency_contacts_view, name='emergency_contacts'),
    path('daily-status/', views.daily_status_page, name='daily_status'),
    path('community/', views.community_view, name='community'),
    path('quiz-start/', views.quiz_start, name='quiz_start'),
    path('safety-check/', views.safety_check_view, name='safety_check'),
    path('api/v1/daily-update/', views.receive_daily_update, name='receive_daily_update'),
    
] 