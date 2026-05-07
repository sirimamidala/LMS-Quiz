from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('logout/', views.logout_user, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('start-quiz/', views.start_quiz, name='start_quiz'),
    path('quiz/<str:topic>/', views.quiz_view, name='quiz'),
    path('api/generate-questions/', views.generate_questions_api, name='generate_questions_api'),
    path('api/submit-quiz/', views.submit_quiz_api, name='submit_quiz_api'),
]
