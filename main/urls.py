from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('trafficAccident/', views.traffic_accident, name='trafficAccident'),
]
