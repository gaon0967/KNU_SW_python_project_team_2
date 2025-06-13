
from django.contrib import admin
from django.urls import path, include

from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard_2/', views.dashboard_2, name='dashboard_2'),
    path('', include('main.urls')),
    path('daily-status/', views.daily_status_page, name='daily_status'),
    path('', include('main.urls')),
]
