from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from .forms import CustomUserCreationForm, ProfileForm, PasswordChangeForm
from .models import CustomUser

def register(request):
    """تسجيل مستخدم جديد"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, _('Registration successful! Welcome to our platform.'))
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'accounts/register.html', context)

@login_required
def profile(request):
    """عرض وتعديل الملف الشخصي"""
    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, request.FILES, instance=request.user)
        password_form = PasswordChangeForm(request.user, request.POST)
        
        if 'update_profile' in request.POST and profile_form.is_valid():
            profile_form.save()
            messages.success(request, _('Profile updated successfully'))
            return redirect('accounts:profile')
        
        elif 'change_password' in request.POST and password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, _('Password changed successfully'))
            return redirect('accounts:profile')
    
    else:
        profile_form = ProfileForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)
    
    context = {
        'profile_form': profile_form,
        'password_form': password_form,
    }
    
    return render(request, 'accounts/profile.html', context)

@login_required
def toggle_dark_mode(request):
    """تبديل الوضع المظلم"""
    if request.method == 'POST' and request.is_ajax():
        user = request.user
        user.dark_mode = not user.dark_mode
        user.save()
        return JsonResponse({'success': True, 'dark_mode': user.dark_mode})
    
    return JsonResponse({'success': False})

@login_required
def dashboard(request):
    """لوحة تحكم المستخدم"""
    # إحصائيات المستخدم
    from courses.models import Enrollment
    from articles.models import Comment
    
    user_enrollments = Enrollment.objects.filter(user=request.user).count()
    user_comments = Comment.objects.filter(email=request.user.email, is_approved=True).count()
    
    # آخر النشاطات
    recent_enrollments = Enrollment.objects.filter(
        user=request.user
    ).select_related('course').order_by('-enrolled_at')[:5]
    
    recent_comments = Comment.objects.filter(
        email=request.user.email,
        is_approved=True
    ).select_related('article').order_by('-created_at')[:5]
    
    context = {
        'user_enrollments': user_enrollments,
        'user_comments': user_comments,
        'recent_enrollments': recent_enrollments,
        'recent_comments': recent_comments,
    }
    
    return render(request, 'accounts/dashboard.html', context)

@login_required
def notifications(request):
    """الإشعارات"""
    # في تطبيق حقيقي، ستكون هناك نموذج للإشعارات
    notifications = []  # قائمة إشعارات وهمية
    
    context = {
        'notifications': notifications,
    }
    
    return render(request, 'accounts/notifications.html', context)