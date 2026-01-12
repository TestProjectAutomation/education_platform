from django.shortcuts import redirect
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from functools import wraps

def premium_required(view_func):
    """ديكور للتحقق من اشتراك مميز"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.has_perm('articles.can_view_premium'):
            return view_func(request, *args, **kwargs)
        messages.info(request, _('This content requires a premium subscription.'))
        return redirect('subscription:plans')
    return wrapper

def track_article_view(view_func):
    """ديكور لتتبع مشاهدات المقال"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        
        if request.method == 'GET' and hasattr(response, 'context_data'):
            article = response.context_data.get('article')
            if article and isinstance(article, Article):
                from .models import ArticleView
                ArticleView.objects.create(
                    article=article,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    session_key=request.session.session_key or 'anonymous'
                )
        
        return response
    return wrapper

def staff_required(view_func):
    """ديكور للتحقق من صلاحيات الموظفين"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_staff:
            return view_func(request, *args, **kwargs)
        messages.error(request, _('Access denied. Staff privileges required.'))
        return redirect('home')
    return wrapper