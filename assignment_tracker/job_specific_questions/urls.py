from django.urls import path
from . import views

urlpatterns = [
    path('test', views.test, name='test'),
    path('create/<str:job_id>',views.create_question,name='create_question'),
    path('screening/<str:job_id>',views.show_all_questions,name='show_all_questions'),
    path('answer/<str:talent_id>/<str:question_id>',views.answer,name='answer'),
]