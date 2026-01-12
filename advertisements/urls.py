from django.urls import path
from . import views

app_name = 'advertisements'

urlpatterns = [
    path('impression/<int:ad_id>/', views.record_impression, name='record_impression'),
    path('click/<int:ad_id>/', views.record_click, name='record_click'),
    path('dashboard/', views.ad_dashboard, name='dashboard'),
    path('create/', views.create_ad, name='create'),
    path('edit/<int:pk>/', views.edit_ad, name='edit'),
    path('placements/', views.manage_placements, name='placements'),
    path('toggle/<int:pk>/', views.toggle_ad_status, name='toggle_status'),
    path('delete/<int:pk>/', views.delete_ad, name='delete'),
]