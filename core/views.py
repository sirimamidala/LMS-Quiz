from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .models import QuizAttempt, QuizQuestion
from .gemini_service import generate_mcqs
from django.http import JsonResponse
import json
from django.db.models import Avg

def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')

        if password != password_confirm:
            messages.error(request, "Passwords do not match")
            return render(request, 'core/register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return render(request, 'core/register.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        messages.success(request, f"Welcome, {username}! Your account has been created.")
        return redirect('dashboard')
    
    return render(request, 'core/register.html')

def login_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Invalid username or password")
    return render(request, 'core/login.html')

def logout_user(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    attempts = request.user.attempts.all().order_by('-created_at')
    avg_score = attempts.aggregate(Avg('score'))['score__avg'] or 0
    if attempts.exists():
        avg_score = (avg_score / 30) * 100
    return render(request, 'core/dashboard.html', {'attempts': attempts, 'avg_score': avg_score})

@login_required
def start_quiz(request):
    if request.method == 'POST':
        topic = request.POST.get('topic')
        return redirect('quiz', topic=topic)
    return render(request, 'core/start_quiz.html')

@login_required
def quiz_view(request, topic):
    return render(request, 'core/quiz.html', {'topic': topic})

@login_required
def generate_questions_api(request):
    topic = request.GET.get('topic')
    if not topic:
        return JsonResponse({'status': 'error', 'message': 'Topic is required'}, status=400)
    
    questions = generate_mcqs(topic)
    if not questions:
        return JsonResponse({'status': 'error', 'message': 'Failed to generate questions'}, status=500)
    
    return JsonResponse({'status': 'success', 'questions': questions})

@login_required
def submit_quiz_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        topic = data.get('topic')
        answers = data.get('answers')
        questions = data.get('questions')
        
        score = 0
        total = len(questions)
        
        attempt = QuizAttempt.objects.create(
            user=request.user,
            topic=topic,
            total_questions=total
        )
        
        for i, q_data in enumerate(questions):
            selected = str(answers.get(str(i), "")).upper()
            correct = str(q_data.get('answer', "")).upper()
            is_correct = (selected == correct)
            if is_correct:
                score += 1
            
            QuizQuestion.objects.create(
                attempt=attempt,
                question_text=q_data.get('question'),
                option_a=q_data.get('a'),
                option_b=q_data.get('b'),
                option_c=q_data.get('c'),
                option_d=q_data.get('d'),
                correct_answer=correct,
                selected_answer=selected,
                is_correct=is_correct
            )
        
        attempt.score = score
        attempt.save()
        return JsonResponse({'status': 'success', 'score': score, 'total': total})
    
    return JsonResponse({'status': 'error'}, status=400)
