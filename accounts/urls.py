# accounts/urls.py
from django.urls import path, include
from . import views

app_name = 'accounts'

urlpatterns = [
    # ========== Authentication ==========
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # ========== Profile ==========
    path('profile/', views.profile_view, name='profile'),
    path('profile/picture/delete/', views.delete_profile_picture, name='delete_profile_picture'),
    path('profile/<str:username>/', views.public_profile, name='public_profile'),
    
    # ========== Dashboard ==========
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # ========== Settings ==========
    path('settings/', views.settings_view, name='settings'),
    path('settings/dark-mode/', views.toggle_dark_mode, name='toggle_dark_mode'),
    
    # ========== Notifications ==========
    path('notifications/', views.notifications_view, name='notifications'),
    path('notifications/<int:notification_id>/read/', views.mark_notification_read, name='mark_notification_read'),
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),
    path('notifications/<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    
    # ========== Achievements ==========
    path('achievements/', views.achievements_view, name='achievements'),
    
    # ========== Learning Goals ==========
    path('goals/', views.learning_goals_view, name='learning_goals'),
    path('goals/create/', views.create_learning_goal, name='create_learning_goal'),
    path('goals/<int:goal_id>/update/', views.update_learning_goal, name='update_learning_goal'),
    path('goals/<int:goal_id>/delete/', views.delete_learning_goal, name='delete_learning_goal'),
    
    # ========== Bookmarks ==========
    path('bookmarks/', views.bookmarks_view, name='bookmarks'),
    path('bookmarks/add/', views.add_bookmark, name='add_bookmark'),
    path('bookmarks/<int:bookmark_id>/remove/', views.remove_bookmark, name='remove_bookmark'),
    
    # ========== Activity ==========
    path('activity/', views.activity_view, name='activity'),
    
    # ========== API Endpoints ==========
    path('api/upload-profile-picture/', views.upload_profile_picture, name='upload_profile_picture'),
    path('api/update-profile/', views.api_update_profile, name='api_update_profile'),
    path('api/stats/', views.api_get_stats, name='api_get_stats'),
    path('api/activities/<int:limit>/', views.api_get_activities, name='api_get_activities'),
    path('api/activities/', views.api_get_activities, name='api_get_activities_default'),
    
    # ========== Data Export ==========
    path('export-data/', views.export_data, name='export_data'),
    
    # ========== Admin Views ==========
    path('admin/users/', views.user_list, name='user_list'),
    path('admin/users/<int:user_id>/', views.admin_user_detail, name='admin_user_detail'),
    
    # ========== Social Auth (if using allauth) ==========
    # path('social/', include('allauth.urls')),
]