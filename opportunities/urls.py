from django.urls import path
from . import views

app_name = 'opportunities'

urlpatterns = [
    # Vacancies
    path('vacancies/', views.vacancy_list, name='vacancy_list'),
    path('vacancies/<slug:slug>/', views.vacancy_detail, name='vacancy_detail'),
    # Internships
    path('internships/', views.internship_list, name='internship_list'),
    path('internships/<slug:slug>/', views.internship_detail, name='internship_detail'),
    # Grants
    path('grants/', views.grant_list, name='grant_list'),
    path('grants/<slug:slug>/', views.grant_detail, name='grant_detail'),
]
