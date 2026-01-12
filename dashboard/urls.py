from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_index, name='index'),
    path('content/', views.content_management, name='content'),
    path('content/create/', views.create_content, name='create_content'),
    path('content/edit/<str:content_type>/<int:pk>/', views.edit_content, name='edit_content'),
    path('content/delete/<str:content_type>/<int:pk>/', views.delete_content, name='delete_content'),
    path('comments/', views.comment_management, name='comments'),
    path('comments/approve/<int:pk>/', views.approve_comment, name='approve_comment'),
    path('comments/delete/<int:pk>/', views.delete_comment, name='delete_comment'),
    path('users/', views.user_management, name='users'),
    path('users/edit/<int:pk>/', views.edit_user, name='edit_user'),
    path('settings/', views.site_settings, name='settings'),
    path('analytics/', views.analytics, name='analytics'),
]