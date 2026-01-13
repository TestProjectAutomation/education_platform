from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils import timezone
from django.conf import settings
import json
from datetime import timedelta

from .models import (
    CustomUser, UserActivity, UserNotification, 
    Achievement, UserAchievement, LearningGoal, Bookmark
)
from .forms import (
    CustomUserCreationForm, ProfileForm, 
    CustomPasswordChangeForm, LoginForm
)

# ========== Authentication Views ==========

@csrf_protect
def login_view(request):
    """View for user login"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            # Try to authenticate
            user = authenticate(request, username=username, password=password)
            
            # If authentication fails, try email
            if user is None:
                try:
                    user_obj = CustomUser.objects.get(email=username)
                    user = authenticate(request, username=user_obj.username, password=password)
                except CustomUser.DoesNotExist:
                    pass
            
            if user is not None:
                login(request, user)
                
                # Handle remember me
                if not remember_me:
                    request.session.set_expiry(0)  # Browser close
                
                # Log activity
                UserActivity.objects.create(
                    user=user,
                    activity_type='login',
                    description=_('User logged in'),
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                # Success message
                messages.success(request, _('Welcome back, {}!').format(user.get_display_name()))
                
                # Redirect to next or dashboard
                next_url = request.GET.get('next', 'accounts:dashboard')
                return redirect(next_url)
            else:
                messages.error(request, _('Invalid username or password.'))
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {
        'form': form,
        'hide_navbar': True,
        'hide_footer': True,
    })

@login_required
def logout_view(request):
    """View for user logout"""
    # Log activity
    UserActivity.objects.create(
        user=request.user,
        activity_type='logout',
        description=_('User logged out'),
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    logout(request)
    messages.info(request, _('You have been logged out successfully.'))
    return redirect('core:home')

@csrf_protect
def register_view(request):
    """View for user registration"""
    if request.user.is_authenticated:
        return redirect('accounts:dashboard')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            
            # Log the user in
            login(request, user)
            
            # Log activity
            UserActivity.objects.create(
                user=user,
                activity_type='profile_update',
                description=_('New user registration'),
                ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                metadata={'action': 'registration'}
            )
            
            # Send welcome notification
            UserNotification.objects.create(
                user=user,
                notification_type='success',
                title=_('Welcome to {}!').format(settings.SITE_NAME),
                message=_('Thank you for registering. Start your learning journey now!'),
                icon='fas fa-heart',
                action_url='accounts:dashboard'
            )
            
            # Add welcome points
            user.add_points(50)
            
            messages.success(request, _('Registration successful! Welcome to {}.').format(settings.SITE_NAME))
            return redirect('accounts:dashboard')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {
        'form': form,
        'hide_navbar': True,
        'hide_footer': True,
    })

# ========== Profile Views ==========

@login_required
def profile_view(request):
    """View for user profile"""
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            profile_form = ProfileForm(request.POST, request.FILES, instance=request.user)
            if profile_form.is_valid():
                user = profile_form.save()
                
                # Log activity
                UserActivity.objects.create(
                    user=user,
                    activity_type='profile_update',
                    description=_('Profile information updated'),
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                messages.success(request, _('Profile updated successfully'))
                return redirect('accounts:profile')
        
        elif 'change_password' in request.POST:
            password_form = CustomPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                
                # Log activity
                UserActivity.objects.create(
                    user=user,
                    activity_type='profile_update',
                    description=_('Password changed'),
                    ip_address=get_client_ip(request),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    metadata={'action': 'password_change'}
                )
                
                # Send notification
                UserNotification.objects.create(
                    user=user,
                    notification_type='success',
                    title=_('Password Updated'),
                    message=_('Your password has been changed successfully.'),
                    icon='fas fa-lock',
                    action_url='accounts:profile'
                )
                
                messages.success(request, _('Password changed successfully'))
                return redirect('accounts:profile')
    else:
        profile_form = ProfileForm(instance=request.user)
        password_form = CustomPasswordChangeForm(request.user)
    
    # Get user stats
    context = {
        'profile_form': profile_form,
        'password_form': password_form,
        'profile_completion': request.user.profile_completion_percentage(),
        'user_stats': get_user_stats(request.user),
        'recent_activities': UserActivity.objects.filter(user=request.user)[:10],
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
@require_http_methods(["POST"])
def delete_profile_picture(request):
    """Delete user profile picture"""
    if request.user.profile_picture:
        request.user.profile_picture.delete(save=False)
        request.user.profile_picture = None
        request.user.save()
        
        # Log activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='profile_update',
            description=_('Profile picture removed'),
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        messages.success(request, _('Profile picture removed successfully'))
    
    return redirect('accounts:profile')

@login_required
def public_profile(request, username):
    """View for public user profile"""
    user = get_object_or_404(CustomUser, username=username)
    
    # Only show limited information for other users
    if request.user != user:
        context = {
            'profile_user': user,
            'is_owner': False,
            'show_limited': True,
        }
    else:
        context = {
            'profile_user': user,
            'is_owner': True,
            'show_limited': False,
            'user_stats': get_user_stats(user),
            'recent_activities': UserActivity.objects.filter(user=user)[:5],
        }
    
    return render(request, 'accounts/public_profile.html', context)

# ========== Dashboard Views ==========

@login_required
def dashboard_view(request):
    """Main dashboard view"""
    user = request.user
    
    # Get user statistics
    stats = get_user_stats(user)
    
    # Get recent activities
    recent_activities = UserActivity.objects.filter(user=user)[:10]
    
    # Get active courses (you'll need to adapt this to your Course model)
    # active_courses = user.enrollment_set.filter(completed=False).select_related('course')[:5]
    
    # Get upcoming deadlines (you'll need to adapt this to your Course model)
    # upcoming_deadlines = Assignment.objects.filter(
    #     enrollment__user=user,
    #     due_date__gte=timezone.now()
    # ).order_by('due_date')[:5]
    
    # Get learning goals
    learning_goals = LearningGoal.objects.filter(
        user=user,
        status='active'
    ).order_by('-created_at')[:5]
    
    # Get notifications
    notifications = UserNotification.objects.filter(
        user=user,
        is_read=False
    ).order_by('-created_at')[:10]
    
    # Get achievements
    achievements = UserAchievement.objects.filter(
        user=user,
        is_unlocked=True
    ).order_by('-unlocked_at')[:6]
    
    # Get bookmarks
    bookmarks = Bookmark.objects.filter(user=user).order_by('-created_at')[:5]
    
    context = {
        'user': user,
        'stats': stats,
        'recent_activities': recent_activities,
        'learning_goals': learning_goals,
        'notifications': notifications,
        'achievements': achievements,
        'bookmarks': bookmarks,
        'profile_completion': user.profile_completion_percentage(),
        # 'active_courses': active_courses,
        # 'upcoming_deadlines': upcoming_deadlines,
    }
    
    return render(request, 'accounts/dashboard.html', context)

# ========== Settings Views ==========

@login_required
def settings_view(request):
    """User settings view"""
    if request.method == 'POST':
        if 'update_preferences' in request.POST:
            # Update notification preferences
            request.user.email_notifications = 'email_notifications' in request.POST
            request.user.sms_notifications = 'sms_notifications' in request.POST
            request.user.newsletter_subscription = 'newsletter_subscription' in request.POST
            request.user.save()
            
            messages.success(request, _('Preferences updated successfully'))
            
        elif 'update_privacy' in request.POST:
            # Update privacy settings
            # Add your privacy fields here
            request.user.save()
            
            messages.success(request, _('Privacy settings updated'))
    
    return render(request, 'accounts/settings.html', {
        'user': request.user,
    })

@login_required
def toggle_dark_mode(request):
    """Toggle dark mode"""
    if request.method == 'POST':
        request.user.dark_mode = not request.user.dark_mode
        request.user.save()
        
        # Set session variable for immediate effect
        request.session['dark_mode'] = request.user.dark_mode
        
        return JsonResponse({
            'success': True,
            'dark_mode': request.user.dark_mode
        })
    
    return JsonResponse({'success': False})

# ========== Notification Views ==========

@login_required
def notifications_view(request):
    """View all notifications"""
    notifications = UserNotification.objects.filter(user=request.user)
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/notifications.html', {
        'notifications': page_obj,
        'unread_count': notifications.filter(is_read=False).count(),
    })

@login_required
@require_http_methods(["POST"])
def mark_notification_read(request, notification_id):
    """Mark a notification as read"""
    notification = get_object_or_404(
        UserNotification, 
        id=notification_id, 
        user=request.user
    )
    notification.mark_as_read()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('accounts:notifications')

@login_required
@require_http_methods(["POST"])
def mark_all_notifications_read(request):
    """Mark all notifications as read"""
    UserNotification.objects.filter(
        user=request.user,
        is_read=False
    ).update(is_read=True)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    return redirect('accounts:notifications')

@login_required
def delete_notification(request, notification_id):
    """Delete a notification"""
    notification = get_object_or_404(
        UserNotification, 
        id=notification_id, 
        user=request.user
    )
    notification.delete()
    
    messages.success(request, _('Notification deleted'))
    return redirect('accounts:notifications')

# ========== Achievement Views ==========

@login_required
def achievements_view(request):
    """View all achievements"""
    # Get unlocked achievements
    unlocked = UserAchievement.objects.filter(
        user=request.user,
        is_unlocked=True
    ).select_related('achievement')
    
    # Get locked achievements
    unlocked_ids = unlocked.values_list('achievement_id', flat=True)
    locked = Achievement.objects.exclude(id__in=unlocked_ids)
    
    # Get achievement stats
    total_achievements = Achievement.objects.filter(is_active=True).count()
    unlocked_count = unlocked.count()
    total_points = sum(ua.achievement.points for ua in unlocked)
    
    return render(request, 'accounts/achievements.html', {
        'unlocked_achievements': unlocked,
        'locked_achievements': locked,
        'stats': {
            'total': total_achievements,
            'unlocked': unlocked_count,
            'percentage': int((unlocked_count / total_achievements * 100)) if total_achievements > 0 else 0,
            'points': total_points,
        }
    })

# ========== Learning Goals Views ==========

@login_required
def learning_goals_view(request):
    """View all learning goals"""
    goals = LearningGoal.objects.filter(user=request.user)
    
    # Filter by status
    status = request.GET.get('status')
    if status in ['active', 'completed', 'failed', 'paused']:
        goals = goals.filter(status=status)
    
    return render(request, 'accounts/learning_goals.html', {
        'goals': goals,
        'active_count': goals.filter(status='active').count(),
        'completed_count': goals.filter(status='completed').count(),
    })

@login_required
@require_http_methods(["POST"])
def create_learning_goal(request):
    """Create a new learning goal"""
    title = request.POST.get('title')
    description = request.POST.get('description', '')
    target_date = request.POST.get('target_date')
    
    if title:
        goal = LearningGoal.objects.create(
            user=request.user,
            title=title,
            description=description,
            target_date=target_date if target_date else None
        )
        
        # Log activity
        UserActivity.objects.create(
            user=request.user,
            activity_type='profile_update',
            description=_('Created learning goal: {}').format(title),
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            metadata={'goal_id': goal.id}
        )
        
        messages.success(request, _('Learning goal created successfully'))
    
    return redirect('accounts:learning_goals')

@login_required
@require_http_methods(["POST"])
def update_learning_goal(request, goal_id):
    """Update a learning goal"""
    goal = get_object_or_404(LearningGoal, id=goal_id, user=request.user)
    
    title = request.POST.get('title')
    description = request.POST.get('description')
    target_date = request.POST.get('target_date')
    status = request.POST.get('status')
    
    if title:
        goal.title = title
    if description is not None:
        goal.description = description
    if target_date is not None:
        goal.target_date = target_date if target_date else None
    if status in ['active', 'completed', 'failed', 'paused']:
        goal.status = status
    
    goal.save()
    
    return JsonResponse({'success': True})

@login_required
@require_http_methods(["POST"])
def delete_learning_goal(request, goal_id):
    """Delete a learning goal"""
    goal = get_object_or_404(LearningGoal, id=goal_id, user=request.user)
    goal.delete()
    
    messages.success(request, _('Learning goal deleted'))
    return redirect('accounts:learning_goals')

# ========== Bookmark Views ==========

@login_required
def bookmarks_view(request):
    """View all bookmarks"""
    bookmarks = Bookmark.objects.filter(user=request.user)
    
    # Filter by content type
    content_type = request.GET.get('type')
    if content_type in ['course', 'lesson', 'article', 'video', 'quiz']:
        bookmarks = bookmarks.filter(content_type=content_type)
    
    # Group by content type
    bookmarks_by_type = {}
    for bookmark in bookmarks:
        if bookmark.content_type not in bookmarks_by_type:
            bookmarks_by_type[bookmark.content_type] = []
        bookmarks_by_type[bookmark.content_type].append(bookmark)
    
    return render(request, 'accounts/bookmarks.html', {
        'bookmarks': bookmarks,
        'bookmarks_by_type': bookmarks_by_type,
    })

@login_required
@require_http_methods(["POST"])
def add_bookmark(request):
    """Add a new bookmark"""
    content_type = request.POST.get('content_type')
    object_id = request.POST.get('object_id')
    title = request.POST.get('title')
    url = request.POST.get('url')
    thumbnail = request.POST.get('thumbnail', '')
    
    if all([content_type, object_id, title, url]):
        # Check if already bookmarked
        existing = Bookmark.objects.filter(
            user=request.user,
            content_type=content_type,
            object_id=object_id
        ).first()
        
        if not existing:
            Bookmark.objects.create(
                user=request.user,
                content_type=content_type,
                object_id=object_id,
                title=title,
                url=url,
                thumbnail=thumbnail
            )
            
            return JsonResponse({'success': True, 'action': 'added'})
        else:
            # Remove if already exists
            existing.delete()
            return JsonResponse({'success': True, 'action': 'removed'})
    
    return JsonResponse({'success': False})

@login_required
@require_http_methods(["POST"])
def remove_bookmark(request, bookmark_id):
    """Remove a bookmark"""
    bookmark = get_object_or_404(Bookmark, id=bookmark_id, user=request.user)
    bookmark.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True})
    
    messages.success(request, _('Bookmark removed'))
    return redirect('accounts:bookmarks')

# ========== Activity Views ==========

@login_required
def activity_view(request):
    """View all user activities"""
    activities = UserActivity.objects.filter(user=request.user)
    
    # Filter by type
    activity_type = request.GET.get('type')
    if activity_type:
        activities = activities.filter(activity_type=activity_type)
    
    # Filter by date
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        activities = activities.filter(created_at__date__gte=date_from)
    if date_to:
        activities = activities.filter(created_at__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(activities, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Activity stats
    stats = {
        'total': activities.count(),
        'today': activities.filter(created_at__date=timezone.now().date()).count(),
        'this_week': activities.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).count(),
        'this_month': activities.filter(
            created_at__month=timezone.now().month,
            created_at__year=timezone.now().year
        ).count(),
    }
    
    return render(request, 'accounts/activity.html', {
        'activities': page_obj,
        'stats': stats,
        'activity_types': UserActivity.ACTIVITY_TYPES,
    })

# ========== Utility Functions ==========

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def get_user_stats(user):
    """Get comprehensive user statistics"""
    # You'll need to adapt these based on your actual models
    stats = {
        'total_courses': 0,  # user.enrollment_set.count()
        'completed_courses': 0,  # user.enrollment_set.filter(completed=True).count()
        'active_courses': 0,  # user.enrollment_set.filter(completed=False).count()
        'total_points': user.points,
        'level': user.level,
        'experience': user.experience,
        'achievements': user.user_achievements.filter(is_unlocked=True).count(),
        'learning_hours': 0,  # Calculate from your models
        'certificates': 0,  # user.certificate_set.count()
        'bookmarks': user.bookmarks.count(),
        'goals_active': user.learning_goals.filter(status='active').count(),
        'goals_completed': user.learning_goals.filter(status='completed').count(),
        'streak_days': 0,  # Calculate login streak
        'rank': 'Beginner',  # Calculate based on points
    }
    return stats

@login_required
@csrf_exempt
def upload_profile_picture(request):
    """AJAX endpoint for profile picture upload"""
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        user = request.user
        profile_picture = request.FILES['profile_picture']
        
        # Validate file size (max 5MB)
        if profile_picture.size > 5 * 1024 * 1024:
            return JsonResponse({
                'success': False,
                'error': _('File size must be less than 5MB')
            })
        
        # Validate file type
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        if profile_picture.content_type not in allowed_types:
            return JsonResponse({
                'success': False,
                'error': _('Invalid file type. Allowed: JPG, PNG, GIF, WebP')
            })
        
        # Save the file
        user.profile_picture = profile_picture
        user.save()
        
        # Log activity
        UserActivity.objects.create(
            user=user,
            activity_type='profile_update',
            description=_('Profile picture updated'),
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return JsonResponse({
            'success': True,
            'profile_picture_url': user.get_profile_picture_url(),
            'message': _('Profile picture updated successfully')
        })
    
    return JsonResponse({'success': False, 'error': _('Invalid request')})

@login_required
def export_data(request):
    """Export user data in JSON format"""
    user = request.user
    
    # Prepare data for export
    data = {
        'user_info': {
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'date_joined': user.date_joined.isoformat(),
            'last_login': user.last_login.isoformat() if user.last_login else None,
        },
        'activities': list(UserActivity.objects.filter(user=user).values(
            'activity_type', 'description', 'created_at'
        )[:100]),
        'achievements': list(UserAchievement.objects.filter(
            user=user, is_unlocked=True
        ).values('achievement__name', 'unlocked_at')),
        'learning_goals': list(LearningGoal.objects.filter(user=user).values(
            'title', 'status', 'progress', 'created_at'
        )),
        'bookmarks': list(Bookmark.objects.filter(user=user).values(
            'title', 'content_type', 'url', 'created_at'
        )),
    }
    
    # Create JSON response
    response = JsonResponse(data, json_dumps_params={'indent': 2})
    response['Content-Disposition'] = f'attachment; filename="{user.username}_data.json"'
    
    return response

# ========== API Views (for AJAX calls) ==========

@login_required
@csrf_exempt
def api_update_profile(request):
    """API endpoint for profile updates"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = request.user
            
            # Update allowed fields
            allowed_fields = ['first_name', 'last_name', 'bio', 'phone', 
                            'country', 'city', 'address']
            
            for field in allowed_fields:
                if field in data:
                    setattr(user, field, data[field])
            
            user.save()
            
            return JsonResponse({
                'success': True,
                'message': _('Profile updated successfully'),
                'profile_completion': user.profile_completion_percentage()
            })
        
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': _('Invalid JSON')})
    
    return JsonResponse({'success': False, 'error': _('Invalid request method')})

@login_required
def api_get_stats(request):
    """API endpoint for getting user stats"""
    stats = get_user_stats(request.user)
    return JsonResponse(stats)

@login_required
def api_get_activities(request, limit=10):
    """API endpoint for getting recent activities"""
    activities = UserActivity.objects.filter(
        user=request.user
    ).order_by('-created_at')[:limit]
    
    data = []
    for activity in activities:
        data.append({
            'type': activity.activity_type,
            'description': activity.description,
            'time': activity.created_at.strftime('%Y-%m-%d %H:%M'),
            'icon': get_activity_icon(activity.activity_type),
        })
    
    return JsonResponse({'activities': data})

def get_activity_icon(activity_type):
    """Get icon for activity type"""
    icons = {
        'login': 'fas fa-sign-in-alt',
        'logout': 'fas fa-sign-out-alt',
        'course_enroll': 'fas fa-book-open',
        'course_complete': 'fas fa-graduation-cap',
        'profile_update': 'fas fa-user-edit',
        'comment': 'fas fa-comment',
        'like': 'fas fa-heart',
        'share': 'fas fa-share-alt',
        'certificate': 'fas fa-certificate',
        'achievement': 'fas fa-trophy',
    }
    return icons.get(activity_type, 'fas fa-bell')

# ========== Error Handlers ==========

def handler404(request, exception):
    """Custom 404 handler"""
    return render(request, 'accounts/404.html', status=404)

def handler500(request):
    """Custom 500 handler"""
    return render(request, 'accounts/500.html', status=500)

# ========== Admin Views ==========

@login_required
def user_list(request):
    """Admin view for user list (only for admins)"""
    if not request.user.is_superuser and request.user.user_type != 'admin':
        messages.error(request, _('You do not have permission to view this page.'))
        return redirect('accounts:dashboard')
    
    users = CustomUser.objects.all().order_by('-date_joined')
    
    # Search
    query = request.GET.get('q')
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    
    # Filter by user type
    user_type = request.GET.get('type')
    if user_type:
        users = users.filter(user_type=user_type)
    
    # Pagination
    paginator = Paginator(users, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'accounts/admin/user_list.html', {
        'users': page_obj,
        'user_types': CustomUser.USER_TYPE_CHOICES,
    })

@login_required
def admin_user_detail(request, user_id):
    """Admin view for user detail"""
    if not request.user.is_superuser and request.user.user_type != 'admin':
        messages.error(request, _('You do not have permission to view this page.'))
        return redirect('accounts:dashboard')
    
    user = get_object_or_404(CustomUser, id=user_id)
    
    return render(request, 'accounts/admin/user_detail.html', {
        'profile_user': user,
        'activities': UserActivity.objects.filter(user=user)[:20],
        'notifications': UserNotification.objects.filter(user=user)[:10],
    })