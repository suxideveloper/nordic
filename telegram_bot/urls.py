from django.urls import path
from . import views

app_name = 'telegram_bot'

urlpatterns = [
    path('webhook/<str:token_hash>/', views.telegram_webhook, name='webhook'),
]
