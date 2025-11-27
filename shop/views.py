import openpyxl
from io import BytesIO
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User, auth
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm, QuestionForm, ExamForm, StudyMaterialForm, TopicForm
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import get_user_model
from .models import CustomUser, Exam, Question, Attempt, StudentAnswer, Subject, StudyMaterial, Topic



def is_teacher(user):
    return user.is_staff

# LESSON
@login_required(login_url='login')
def home(request):
    exams = Exam.objects.all()
    return render(request, 'index.html', {'exams': exams})


@login_required(login_url='login')
def about(request):
    return render(request, 'about.html')

@login_required(login_url='login')
def contactus(request):
    return render(request, 'contactUs.html')

@login_required(login_url='login')
def topic_list(request):
    topics = Topic.objects.all().order_by('name')
    return render(request, 'topic_list.html', {'topics': topics})

@login_required
def study_material_list(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    materials = topic.materials.all().order_by('-uploaded_at')
    return render(request, 'study_material_list.html', {'topic': topic, 'materials': materials})

@login_required(login_url='login')
def upload_study_material(request):
    if not request.user.is_staff:
        messages.error(request, "Only teachers can upload study materials.")
        return redirect('topic_list')

    if request.method == 'POST':
        form = StudyMaterialForm(request.POST, request.FILES)
        if form.is_valid():
            material = form.save(commit=False)
            material.uploaded_by = request.user
            material.save()
            messages.success(request, "PDF uploaded successfully.")
            return redirect('topic_list')
    else:
        form = StudyMaterialForm()
    return render(request, 'upload_material.html', {'form': form})

@login_required(login_url='login')
def add_topic(request):
    if not request.user.is_staff:
        return redirect('topic_list')

    if request.method == "POST":
        form = TopicForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Topic added successfully.")
            return redirect('topic_list')
    else:
        form = TopicForm()
    return render(request, 'add_topic.html', {'form': form})






# modification

@login_required(login_url='login')
def create_post(request):
    if request.method == 'POST':
        form = ExamForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            return redirect('exam_by_subject')
    else:
        form = ExamForm()
    return render(request, 'post_form.html', {'form': form})

@login_required(login_url='login')
def update_post(request, pk):
    post = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        form = ExamForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            return redirect('exam_by_subject')
    else:
        form = ExamForm(instance=post)
    return render(request, 'post_form.html', {'form': form})

@login_required(login_url='login')
def delete_post(request, pk):
    post = get_object_or_404(Exam, pk=pk)
    if request.method == 'POST':
        post.delete()
        return redirect('exam_by_subject')
    return render(request, 'delete.html', {'post': post})





# STUDENT EXAMINATION
@login_required(login_url='login')
def subject_list(request):
    subjects = Subject.objects.all()
    return render(request, 'subject_list.html', {'subjects': subjects})

@login_required(login_url='login')
def exam_by_subject(request, subject_id):
    subject = get_object_or_404(Subject, id=subject_id)
    exams = Exam.objects.filter(subject=subject)
    return render(request, 'exam_by_subject.html', {'subject': subject, 'exams': exams})


@login_required(login_url='login')
def start_exam(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)

    # If user is a teacher/staff → unlimited attempts, no record
    if request.user.is_staff:
        request.session['attempt_id'] = None  # No DB record
        return redirect('exam_questions', exam_id=exam.id, question_number=1)

    # If user is a student → max 4 attempts, record each one
    previous_attempts = Attempt.objects.filter(student=request.user, exam=exam).count()
    if previous_attempts >= 4:
        return render(request, 'limit_reached.html')

    attempt = Attempt.objects.create(
        student=request.user,
        exam=exam,
        attempt_number=previous_attempts + 1
    )
    request.session['attempt_id'] = attempt.id
    return redirect('exam_questions', exam_id=exam.id, question_number=1)



@login_required(login_url='login')
def exam_questions(request, exam_id, question_number):
    exam = get_object_or_404(Exam, id=exam_id)
    attempt_id = request.session.get('attempt_id')
    questions = exam.question_set.all()
    total = questions.count()

    # === STAFF FLOW ===
    if request.user.is_staff:
        if question_number > total or question_number < 1:
            # Exam finished → just show result page without saving
            return render(request, 'result.html', {
                'attempt': None,
                'is_staff': True,
                'exam': exam,
                'subject': exam.subject
            })

        question = questions[question_number - 1]

        # Handle navigation for staff
        if request.method == 'POST':
            if 'next' in request.POST:
                return redirect('exam_questions', exam_id=exam.id, question_number=question_number + 1)
            elif 'prev' in request.POST:
                return redirect('exam_questions', exam_id=exam.id, question_number=question_number - 1)
            elif 'submit' in request.POST:
                return render(request, 'result.html', {
                    'attempt': None,
                    'is_staff': True,
                    'exam': exam,
                    'subject': exam.subject
                })

        return render(request, 'question.html', {
            'exam': exam,
            'question': question,
            'current': question_number,
            'total': total,
            'is_staff': True
        })

    # === STUDENT FLOW ===
    attempt = get_object_or_404(Attempt, id=attempt_id)

    if question_number > total or question_number < 1:
        # Finish exam and calculate score
        score = sum(
            1 for ans in StudentAnswer.objects.filter(attempt=attempt)
            if ans.selected_option == ans.question.correct_option
        )
        attempt.score = score
        attempt.save()
        return redirect('exam_result', attempt_id=attempt.id)

    question = questions[question_number - 1]

    if request.method == 'POST':
        selected = request.POST.get('selected_option')
        if selected:
            StudentAnswer.objects.update_or_create(
                attempt=attempt,
                question=question,
                defaults={'selected_option': selected}
            )

        if 'next' in request.POST:
            return redirect('exam_questions', exam_id=exam_id, question_number=question_number + 1)
        elif 'prev' in request.POST:
            return redirect('exam_questions', exam_id=exam_id, question_number=question_number - 1)
        elif 'submit' in request.POST:
            score = sum(
                1 for ans in StudentAnswer.objects.filter(attempt=attempt)
                if ans.selected_option == ans.question.correct_option
            )
            attempt.score = score
            attempt.save()
            return redirect('exam_result', attempt_id=attempt.id)

    return render(request, 'question.html', {
        'exam': exam,
        'question': question,
        'current': question_number,
        'total': total
    })



@login_required(login_url='login')
def exam_result(request, attempt_id):
    attempt = get_object_or_404(Attempt, id=attempt_id)
    return render(request, 'result.html', {'attempt': attempt})


@login_required(login_url='login')
def student_history(request):
    attempts = Attempt.objects.filter(student=request.user).order_by('-timestamp')
    return render(request, 'student_history.html', {'attempts': attempts})

@user_passes_test(is_teacher)
@login_required(login_url='login')
def teacher_exam_results(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    attempts = Attempt.objects.filter(exam=exam).order_by('student', 'attempt_number')
    return render(request, 'teacher_exam_results.html', {'exam': exam, 'attempts': attempts})

@user_passes_test(is_teacher)
@login_required(login_url='login')
def add_question(request, exam_id):
    exam = get_object_or_404(Exam, id=exam_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.exam = exam
            question.save()
            return redirect('teacher_exam_results', exam_id=exam.id)
    else:
        form = QuestionForm() 
    return render(request, 'add_question.html', {'form': form, 'exam': exam})


@user_passes_test(is_teacher)
@login_required(login_url='login')
def edit_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    if request.method == 'POST':
        form = QuestionForm(request.POST, instance=question)
        if form.is_valid():
            form.save()
            return redirect('teacher_exam_results', exam_id=question.exam.id)
    else:
        form = QuestionForm(instance=question)
    return render(request, 'edit_question.html', {'form': form, 'exam': question.exam})
    
@user_passes_test(is_teacher)
@login_required(login_url='login')
def delete_question(request, question_id):
    question = get_object_or_404(Question, id=question_id)
    exam_id = question.exam.id
    if request.method == 'POST':
        question.delete()
        return redirect('exam_by_subject', exam_id=exam_id)
    
    return render(request, 'delete_question.html', {'question': question})


@login_required(login_url='login')
def download_exam_result_excel(request, exam_id):
    # get exam for filename/context
    exam = get_object_or_404(Exam, id=exam_id)
    exam_attempts = Attempt.objects.filter(exam_id=exam_id).select_related('student', 'exam')
    
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = "Exam Results"
    
    headers = ["Student Username", "School", "Gender", "Exam Title", "Attempt #", "Score", "Date"]
    sheet.append(headers)
    
    for attempt in exam_attempts:
        sheet.append([
            attempt.student.username,
            attempt.student.school,
            attempt.student.gender,
            attempt.exam.title,
            attempt.attempt_number,
            attempt.score,
            attempt.timestamp.strftime("%Y-%m-%d")
        ])
    
    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)
    
    filename = f"{exam.title}_result.xlsx"
    response = HttpResponse(
        buffer.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    return response

# USER AUTHENTICATION

User = get_user_model()

def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            if User.objects.filter(username=username).exists():
                form.add_error('username', 'This username is already taken.')
            else:
                user = form.save(commit=False)
                user.set_unusable_password()
                user.save()
                auth_login(request, user)
                return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'signup.html', {'form': form})



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        school = request.POST.get('school')
        occupation = request.POST.get('occupation')
        
        try:
            user = User.objects.get(username=username, school=school, occupation=occupation)
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')
        except User.DoesNotExist:
            return render(request, 'signin.html', {'error': 'Invalid login credentials'})
    return render(request, 'signin.html')



@login_required(login_url='login')
def logout(request):
    auth.logout(request)
    return redirect('login')







