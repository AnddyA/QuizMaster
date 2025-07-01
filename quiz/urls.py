from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'),
    #path('registro/', views.register_student, name='register_student'),
    #path('login/', views.login_student, name='login_student'),
    #path('logout/', views.logout_student, name='logout_student'),
    path('dashboard/', views.dashboard_student, name='dashboard_student'),
    path('grupo/crear/', views.create_group, name='create_group'),
    path('grupo/unirse/', views.join_group, name='join_group'),
    path('grupo/salir/', views.leave_group, name='leave_group'),
    path('quiz/iniciar/', views.start_quiz, name='start_quiz'),
    path('quiz/pregunta/', views.quiz_question, name='quiz_question'),
    path('quiz/resultado/', views.quiz_result, name='quiz_result'),
    path('pregunta/crear/', views.create_question, name='create_question'),
    path('perfil/', views.profile, name='profile'),
    path('grupohistorial/', views.group_history, name='group_history'),
    path('rankings/', views.group_rankings, name='group_rankings'),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
