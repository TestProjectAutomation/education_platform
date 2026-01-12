from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    path('', views.article_list, name='list'),
    path('<slug:slug>/', views.article_detail, name='detail'),
    path('tag/<slug:slug>/', views.article_by_tag, name='tag'),
]