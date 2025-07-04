from django.forms import modelformset_factory
from django.shortcuts import render, redirect
from .forms import *
from .models import *
from django.contrib import messages
from django.utils import timezone
import random
from datetime import datetime
from django.utils.timezone import now
from django.db.models import F, Max, Min
from django.shortcuts import get_object_or_404
from django.http import HttpResponse

def home(request):
    formL = StudentLoginForm()
    formR = StudentRegisterForm()

    if request.method == 'POST':
        action = request.POST.get("action")

        if action == "register":
            formR = StudentRegisterForm(request.POST)
            if formR.is_valid():
                dni = formR.cleaned_data['dni']
                if User.objects.filter(dni=dni).exists():
                    messages.error(request, 'Ya existe un estudiante con esa cédula.')
                    formR = StudentRegisterForm()  # Reset form
                else:
                    formR.save()
                    messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.')

            else:
                messages.error(request, 'Ya existe un estudiante con esa cédula o completa correctamente el formulario de registro.')
                formR = StudentRegisterForm()  # Reset form

        elif action == "login":
            formL = StudentLoginForm(request.POST)
            if formL.is_valid():
                dni = formL.cleaned_data['dni']
                try:
                    student = User.objects.get(dni=dni)
                    request.session['student_id'] = student.id
                    return redirect('dashboard_student')
                except User.DoesNotExist:
                    messages.error(request, 'Cédula no encontrada.')
                    formL = StudentLoginForm()  # Reset form
            else:
                messages.error(request, 'Completa correctamente el formulario de inicio de sesión.')

    return render(request, 'home.html', {
        'formL': formL,
        'formR': formR,
        'now': now()
    })


#def register_student(request, formR):
#    if request.method == 'POST':
#        formR = StudentRegisterForm(request.POST)
#        if formR.is_valid():
#            dni = formR.cleaned_data['dni']
#            if Student.objects.filter(dni=dni).exists():
#                messages.error(request, 'Ya existe un estudiante con esa cédula.')
#            else:
#                formR.save()
#                messages.success(request, 'Registro exitoso. Ahora puedes iniciar sesión.')
#                return redirect('login_student')
#    else:
#        formR = StudentRegisterForm()
#    return render(request, 'register.html', {'form': formR})

#def login_student(request):
#    if request.method == 'POST':
#        form = StudentLoginForm(request.POST)
#        if form.is_valid():
#            dni = form.cleaned_data['dni']
#            try:
#                student = Student.objects.get(dni=dni)
#                request.session['student_id'] = student.id  # Inicia sesión
#                return redirect('dashboard_student')
#            except Student.DoesNotExist:
#                messages.error(request, 'Cédula no encontrada.')
#    else:
#        form = StudentLoginForm()
#    return render(request, 'login.html', {'form': form})

#def logout_student(request):
#    request.session.flush()
#    return redirect('home')


def dashboard_student(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('home')

    student = User.objects.get(id=student_id)
    return render(request, 'dashboard.html', {'student': student})


def create_group(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('home')

    student = User.objects.get(id=student_id)
    
    if student.group_set.exists():
        messages.error(request, 'Ya perteneces a un grupo.')
        return redirect('dashboard_student')

    if request.method == 'POST':
        form = CreateGroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            group.members.add(student)
            messages.success(request, f'Grupo "{group.name}" creado y unido exitosamente.')
            return redirect('dashboard_student')
    else:
        form = CreateGroupForm()
    
    return render(request, 'create_group.html', {'form': form, 'student': student})


def join_group(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('home')

    student = User.objects.get(id=student_id)

    if student.group_set.exists():
        messages.error(request, 'Ya perteneces a un grupo.')
        return redirect('dashboard_student')

    if request.method == 'POST':
        form = JoinGroupForm(request.POST)
        if form.is_valid():
            group_id = form.cleaned_data['group_id']
            
            try:
                group = Group.objects.get(id=group_id)
                if group.members.count() >= 3:
                    messages.error(request, 'El grupo ya tiene 3 miembros.')
                else:
                    group.members.add(student)
                    messages.success(request, f'Te uniste al grupo "{group.name}" correctamente.')
                    return redirect('dashboard_student')
            except Group.DoesNotExist:
                messages.error(request, 'El grupo no existe.')
    else:
        form = JoinGroupForm()

    return render(request, 'join_group.html', {'form': form, 'student': student})


def leave_group(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('home')

    student = User.objects.get(id=student_id)
    groups = student.group_set.all()

    if groups.exists():
        group = groups.first()
        group.members.remove(student)
        #if group.members.count() == 0:
        #    group_name = group.name
        #    group.delete()
        #    messages.success(request, f'Saliste del grupo y como estaba vacío, el grupo "{group_name}" fue eliminado.')
        #else:
        messages.success(request, f'Saliste del grupo "{group.name}".')
    else:
        messages.warning(request, 'No perteneces a ningún grupo.')

    return redirect('dashboard_student')



def start_quiz(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('home')

    student = User.objects.get(id=student_id)
    groups = student.group_set.all()

    if not groups.exists():
        messages.error(request, "Debes pertenecer a un grupo para iniciar una prueba.")
        return redirect('dashboard_student')

    group = groups.first()

    # Crear el quiz
    quiz = Quiz.objects.create(group=group)

    selected_questions = []
    categories = Category.objects.all()

    for category in categories:
        questions = list(Question.objects.filter(category=category))
        selected = random.sample(questions, min(3, len(questions)))
        selected_questions.extend(selected)

    request.session['quiz_id'] = quiz.id
    request.session['question_ids'] = [q.id for q in selected_questions]
    request.session['current_index'] = 0
    request.session['score'] = 0
    request.session['start_time'] = timezone.now().isoformat()

    return redirect('quiz_question')


def quiz_question(request):
    quiz_id = request.session.get('quiz_id')
    question_ids = request.session.get('question_ids', [])
    index = request.session.get('current_index', 0)

    student_id = request.session.get('student_id')
    student = User.objects.get(id=student_id)

    if quiz_id is None or index >= len(question_ids):
        return redirect('quiz_result')

    question = Question.objects.get(id=question_ids[index])
    options = question.options.all()

    points_per_question = 1000 / len(question_ids)

    if request.method == 'POST':
        selected_option_id = request.POST.get('option')

        if selected_option_id:
            selected_option = Option.objects.get(id=selected_option_id)

            QuizAnswer.objects.create(
                quiz_id=quiz_id,
                question=question,
                selected_option=selected_option
            )

            if selected_option.is_correct:
                request.session['score'] += points_per_question
        else:
            # no seleccionó nada, incorrecta
            QuizAnswer.objects.create(
                quiz_id=quiz_id,
                question=question,
                selected_option=None
            )
            # no suma puntos

        request.session['current_index'] += 1
        return redirect('quiz_question')

    return render(request, 'quiz_question.html', {
        'question': question,
        'options': options,
        'category': question.category.name,
        'current': index + 1,
        'total': len(question_ids),
        'student': student
    })


def quiz_result(request):
    quiz_id = request.session.get('quiz_id')
    student_id = request.session.get('student_id')
    student = User.objects.get(id=student_id)

    if quiz_id is None:
        return redirect('dashboard_student')

    quiz = Quiz.objects.get(id=quiz_id)

    score = request.session.get('score', 0)
    quiz.score = score
    quiz.end_time = timezone.now()
    quiz.save()

    start_time_str = request.session.get('start_time')
    end_time = timezone.now()
    time_taken = None

    if start_time_str:
        start_time = datetime.fromisoformat(start_time_str)
        time_taken = end_time - start_time

    group_name = quiz.group.name

    # Limpieza de sesión
    for key in ['quiz_id', 'question_ids', 'current_index', 'score', 'start_time']:
        request.session.pop(key, None)

    return render(request, 'quiz_result.html', {
        'group': group_name,
        'score': score,
        'time_taken': time_taken,
        'student': student
    })

def create_question(request):
    OptionFormSet = modelformset_factory(Option, form=OptionForm, extra=4, max_num=4, validate_max=True)

    if request.method == 'POST':
        q_form = QuestionForm(request.POST, request.FILES)
        formset = OptionFormSet(request.POST)

        if q_form.is_valid() and formset.is_valid():
            question = q_form.save()

            correct_count = 0
            for form in formset:
                option = form.save(commit=False)
                option.question = question
                option.save()
                if option.is_correct:
                    correct_count += 1

            if correct_count != 1:
                question.delete()
                messages.error(request, "Debe marcar exactamente una opción como correcta.")
                return redirect('create_question')

            messages.success(request, "Pregunta y opciones guardadas exitosamente.")
            return redirect('dashboard_student')  # o dashboard_admin si lo usas

    else:
        q_form = QuestionForm()
        formset = OptionFormSet(queryset=Option.objects.none())

    return render(request, 'create_question.html', {
        'q_form': q_form,
        'formset': formset
    })


def profile(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('home')

    student = User.objects.get(id=student_id)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Perfil actualizado correctamente.")
            return redirect('profile')
    else:
        form = ProfileForm(instance=student)

    return render(request, 'profile.html', {
        'student': student,
        'form': form
    })

def group_history(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('home')

    student = User.objects.get(id=student_id)
    group = student.group_set.first()

    if not group:
        messages.error(request, "No perteneces a ningún grupo.")
        return redirect('dashboard_student')

    quizzes = Quiz.objects.filter(group=group).order_by('-end_time')[:5]

    # Calculamos la duración en formato mm:ss
    for quiz in quizzes:
        if quiz.start_time and quiz.end_time:
            delta = quiz.end_time - quiz.start_time
            quiz.duration_str = f"{delta.seconds // 60:02d}:{delta.seconds % 60:02d}"
        else:
            quiz.duration_str = "N/D"

    return render(request, 'group_history.html', {
        'group': group,
        'quizzes': quizzes,
        'student': student
    })

def group_rankings(request):
    student_id = request.session.get('student_id')
    if not student_id:
        return redirect('home')
    student = User.objects.get(id=student_id)

    # sacar todos los grupos que alguna vez han jugado
    group_ids = Quiz.objects.values_list('group', flat=True).distinct()

    best_quizzes = []

    for gid in group_ids:
        # para cada grupo, sacar sus quizzes ordenados primero por mayor score,
        # y si empatan, por menor duración
        quizzes = (
            Quiz.objects
            .filter(group_id=gid, score__isnull=False, end_time__isnull=False)
            .annotate(duration=F('end_time') - F('start_time'))
            .order_by('-score', 'duration')
        )
        if quizzes.exists():
            best_quizzes.append(quizzes.first())

    # ahora ordenar todos los mejores de cada grupo
    best_quizzes.sort(
        key=lambda q: (-q.score, (q.end_time - q.start_time).total_seconds() if q.end_time and q.start_time else float('inf'))
    )

    data = []
    for quiz in best_quizzes:
        if quiz.start_time and quiz.end_time:
            delta = quiz.end_time - quiz.start_time
            duration_str = f"{delta.seconds // 60:02d}:{delta.seconds % 60:02d}"
        else:
            duration_str = "N/D"

        members = quiz.group.members.all()
        member_names = [f"{s.first_name} {s.last_name}" for s in members]

        data.append({
            'group': quiz.group.name,
            'members': member_names,
            'score': quiz.score,
            'duration': duration_str
        })

    return render(request, 'group_rankings.html', {
        'rankings': data,
        'student': student
    })


def manage_groups(request):
    user_id = request.session.get('student_id')  # asegúrate que usas user_id en el login
    if not user_id:
        return redirect('home')
    
    user = User.objects.get(id=user_id)
    if user.role != 'admin':
        messages.error(request, "No tienes permisos para acceder aquí.")
        return redirect('home')
    
    groups = Group.objects.all()
    
    if request.method == 'POST':
        action = request.POST.get('action')
        group_id = request.POST.get('group_id')

        group = get_object_or_404(Group, id=group_id)

        if action == 'rename':
            new_name = request.POST.get('new_name')
            if new_name:
                group.name = new_name
                group.save()
                messages.success(request, "Grupo renombrado correctamente.")
        elif action == 'delete':
            group.delete()
            messages.success(request, "Grupo eliminado correctamente.")
        return redirect('manage_groups')
    
    return render(request, 'manage_groups.html', {'groups': groups, 'student': user})