from django.urls import path
from . import views


urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contactus, name='contact'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout, name='logout'),
    path('update/<int:pk>/', views.update_post, name='update_post'),
    path('delete/<int:pk>/', views.delete_post, name='delete_post'),
    path('create/', views.create_post, name='create_post'),
    path('exam/<int:exam_id>/start/', views.start_exam, name='start_exam'),
    path('exam/<int:exam_id>/question/<int:question_number>/', views.exam_questions, name='exam_questions'),
    path('exam/result/<int:attempt_id>/', views.exam_result, name='exam_result'),
    path('exam/history/', views.student_history, name='student_history'),
    path('exam/<int:exam_id>/results/', views.teacher_exam_results, name='teacher_exam_results'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('subjects/<int:subject_id>/exams/', views.exam_by_subject, name='exam_by_subject'),
    path('exam/<int:exam_id>/add_question/', views.add_question, name='add_question'),
    path('question/<int:question_id>/edit/', views.edit_question, name='edit_question'),
    path('question/<int:question_id>/delete/', views.delete_question, name='delete_question'),
    path('materials/topics/', views.topic_list, name='topic_list'),
    path('materials/<int:topic_id>/', views.study_material_list, name='study_material_list'),
    path('materials/upload/', views.upload_study_material, name='upload_study_material'),
    path('materials/topics/add/', views.add_topic, name='add_topic'),
    path('exam/<int:exam_id>/download/', views.download_exam_result_excel, name='download_exam_result_excel'),

    
]