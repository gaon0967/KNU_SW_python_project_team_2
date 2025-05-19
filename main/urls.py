from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard_2/', views.dashboard_2, name='dashboard_2'),
]
