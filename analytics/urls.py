from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('track/', views.track_time_spent, name='track'),
    path('dashboard/', views.analytics_dashboard, name='dashboard'),
]
