from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.page_list, name='list'),
    path('<slug:slug>/', views.page_detail, name='detail'),
]