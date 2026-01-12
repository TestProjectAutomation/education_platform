from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.translation import gettext_lazy as _
from articles.models import Article, Comment
from courses.models import Course
from books.models import Book 
from scholarships.models import Scholarship
from django.db.models import Count
from datetime import datetime, timedelta

def is_admin_or_editor(user):
    return user.user_type in ['admin', 'editor']

@login_required
@user_passes_test(is_admin_or_editor)
def dashboard_index(request):
    # Get statistics
    today = datetime.now().date()
    last_week = today - timedelta(days=7)
    
    context = {
        'total_articles': Article.objects.count(),
        'total_courses': Course.objects.count(),
        'total_books': Book.objects.count(),
        'total_scholarships': Scholarship.objects.count(),
        'recent_articles': Article.objects.filter(created_at__gte=last_week).count(),
        'pending_comments': Comment.objects.filter(is_approved=False).count(),
        'latest_content': Article.objects.filter(status='published').order_by('-created_at')[:5],
    }
    
    return render(request, 'dashboard/index.html', context)