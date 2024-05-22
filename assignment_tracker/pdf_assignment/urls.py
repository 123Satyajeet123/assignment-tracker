from django.urls import path
from . import views

urlpatterns = [
    path('test', views.test, name='test'),
    # DONE-----------------------------------------------------------------------
    path('create/<str:job_id>',views.create_assignment,name='create_assignment'), 
    # path('assign/all/<str:job_id>',views.assign_all,name="assign_all"),
    path('assign/<str:talent_type>/<str:job_id>',views.assign_all,name="assign_all"),
    path('submit/<str:talent_id>/<str:job_id>',views.submit,name="submit"),
    path('assign/single/<str:talent_id>/<str:job_id>',views.assign_to_talent,name="assign_to_talent"),
    # path('show/<str:job_id>',views.show_assignment,name='show_assignment'),
]