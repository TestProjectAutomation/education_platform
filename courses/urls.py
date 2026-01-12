from django.urls import path
from . import views

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='list'),
    path('<slug:slug>/', views.course_detail, name='detail'),
    path('<int:course_id>/enroll/', views.enroll_course, name='enroll'),
    path('<slug:slug>/review/', views.add_review, name='add_review'),
    path('<slug:slug>/learn/', views.learn_course, name='learn'),
    path('my-courses/', views.my_courses, name='my_courses'),
]