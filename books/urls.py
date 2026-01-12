from django.urls import path
from . import views

app_name = 'books'

urlpatterns = [
    path('', views.book_list, name='list'),
    path('<slug:slug>/', views.book_detail, name='detail'),
    path('<slug:slug>/download/', views.download_book, name='download'),
    path('<slug:slug>/preview/', views.preview_book, name='preview'),
]