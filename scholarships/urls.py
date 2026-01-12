from django.urls import path
from . import views

app_name = 'scholarships'

urlpatterns = [
    path('', views.scholarship_list, name='list'),
    path('<slug:slug>/', views.scholarship_detail, name='detail'),
    path('country/<str:country>/', views.scholarship_country, name='country'),
]