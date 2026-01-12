from articles.models import Article, Comment
from courses.models import Course
from books.models import Book 
from scholarships.models import Scholarship
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db.models import Count, Q
from datetime import datetime, timedelta
from core.forms import *


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



# التحقق من صلاحيات المستخدم
def check_permission(user, required_type='editor'):
    """التحقق من صلاحيات المستخدم"""
    return user.user_type in ['admin', required_type]

@login_required
@user_passes_test(lambda u: check_permission(u))
def content_management(request):
    """إدارة المحتوى"""
    content_type = request.GET.get('type', 'all')
    
    # جلب المحتوى حسب النوع
    if content_type == 'articles':
        from articles.models import Article
        contents = Article.objects.all().order_by('-created_at')
    elif content_type == 'courses':
        from courses.models import Course
        contents = Course.objects.all().order_by('-created_at')
    elif content_type == 'books':
        from books.models import Book
        contents = Book.objects.all().order_by('-created_at')
    elif content_type == 'scholarships':
        from scholarships.models import Scholarship
        contents = Scholarship.objects.all().order_by('-created_at')
    else:
        # جمع كل أنواع المحتوى
        contents = []
    
    # البحث
    query = request.GET.get('q')
    if query:
        if hasattr(contents, 'filter'):
            contents = contents.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query)
            )
    
    # الترقيم
    paginator = Paginator(contents, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'contents': page_obj,
        'content_type': content_type,
        'query': query,
    }
    
    return render(request, 'dashboard/content.html', context)

@login_required
@user_passes_test(lambda u: check_permission(u))
def create_content(request):
    """إنشاء محتوى جديد"""
    content_type = request.GET.get('type', 'article')
    
    if request.method == 'POST':
        if content_type == 'article':
            from articles.forms import ArticleForm
            form = ArticleForm(request.POST, request.FILES)
        elif content_type == 'course':
            from courses.forms import CourseForm
            form = CourseForm(request.POST, request.FILES)
        elif content_type == 'book':
            from books.forms import BookForm
            form = BookForm(request.POST, request.FILES)
        elif content_type == 'scholarship':
            from scholarships.forms import ScholarshipForm
            form = ScholarshipForm(request.POST, request.FILES)
        else:
            messages.error(request, _('Invalid content type'))
            return redirect('dashboard:content')
        
        if form.is_valid():
            content = form.save(commit=False)
            content.author = request.user
            content.save()
            form.save_m2m()  # لحفظ العلاقات Many-to-Many
            
            messages.success(request, _(f'{content_type.title()} created successfully'))
            return redirect('dashboard:content')
    else:
        # تحضير النموذج المناسب
        if content_type == 'article':
            from articles.forms import ArticleForm
            form = ArticleForm()
        elif content_type == 'course':
            from courses.forms import CourseForm
            form = CourseForm()
        elif content_type == 'book':
            from books.forms import BookForm
            form = BookForm()
        elif content_type == 'scholarship':
            from scholarships.forms import ScholarshipForm
            form = ScholarshipForm()
        else:
            messages.error(request, _('Invalid content type'))
            return redirect('dashboard:content')
    
    context = {
        'form': form,
        'content_type': content_type,
    }
    
    return render(request, 'dashboard/create_content.html', context)

@login_required
@user_passes_test(lambda u: check_permission(u))
def edit_content(request, content_type, pk):
    """تعديل المحتوى"""
    # جلب النموذج المناسب
    if content_type == 'article':
        from articles.models import Article
        from articles.forms import ArticleForm
        content = get_object_or_404(Article, pk=pk)
        FormClass = ArticleForm
    elif content_type == 'course':
        from courses.models import Course
        from courses.forms import CourseForm
        content = get_object_or_404(Course, pk=pk)
        FormClass = CourseForm
    elif content_type == 'book':
        from books.models import Book
        from books.forms import BookForm
        content = get_object_or_404(Book, pk=pk)
        FormClass = BookForm
    elif content_type == 'scholarship':
        from scholarships.models import Scholarship
        from scholarships.forms import ScholarshipForm
        content = get_object_or_404(Scholarship, pk=pk)
        FormClass = ScholarshipForm
    else:
        messages.error(request, _('Invalid content type'))
        return redirect('dashboard:content')
    
    if request.method == 'POST':
        form = FormClass(request.POST, request.FILES, instance=content)
        if form.is_valid():
            form.save()
            messages.success(request, _('Content updated successfully'))
            return redirect('dashboard:content')
    else:
        form = FormClass(instance=content)
    
    context = {
        'form': form,
        'content': content,
        'content_type': content_type,
    }
    
    return render(request, 'dashboard/edit_content.html', context)

@login_required
@user_passes_test(lambda u: check_permission(u))
def delete_content(request, content_type, pk):
    """حذف المحتوى"""
    # جلب النموذج المناسب
    if content_type == 'article':
        from articles.models import Article
        content = get_object_or_404(Article, pk=pk)
    elif content_type == 'course':
        from courses.models import Course
        content = get_object_or_404(Course, pk=pk)
    elif content_type == 'book':
        from books.models import Book
        content = get_object_or_404(Book, pk=pk)
    elif content_type == 'scholarship':
        from scholarships.models import Scholarship
        content = get_object_or_404(Scholarship, pk=pk)
    else:
        messages.error(request, _('Invalid content type'))
        return redirect('dashboard:content')
    
    if request.method == 'POST':
        content.delete()
        messages.success(request, _('Content deleted successfully'))
    
    return redirect('dashboard:content')

@login_required
@user_passes_test(lambda u: check_permission(u))
def comment_management(request):
    """إدارة التعليقات"""
    from articles.models import Comment
    
    comments = Comment.objects.all().order_by('-created_at')
    
    # التصفية
    status = request.GET.get('status', 'all')
    if status == 'pending':
        comments = comments.filter(is_approved=False)
    elif status == 'approved':
        comments = comments.filter(is_approved=True)
    
    # البحث
    query = request.GET.get('q')
    if query:
        comments = comments.filter(
            Q(name__icontains=query) |
            Q(content__icontains=query) |
            Q(email__icontains=query)
        )
    
    # الترقيم
    paginator = Paginator(comments, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'comments': page_obj,
        'status': status,
        'query': query,
    }
    
    return render(request, 'dashboard/comments.html', context)

@login_required
@user_passes_test(lambda u: check_permission(u))
def approve_comment(request, pk):
    """الموافقة على تعليق"""
    from articles.models import Comment
    
    comment = get_object_or_404(Comment, pk=pk)
    comment.is_approved = True
    comment.save()
    
    messages.success(request, _('Comment approved successfully'))
    return redirect('dashboard:comments')

@login_required
@user_passes_test(lambda u: check_permission(u))
def delete_comment(request, pk):
    """حذف تعليق"""
    from articles.models import Comment
    
    comment = get_object_or_404(Comment, pk=pk)
    
    if request.method == 'POST':
        comment.delete()
        messages.success(request, _('Comment deleted successfully'))
    
    return redirect('dashboard:comments')

@login_required
@user_passes_test(lambda u: u.user_type == 'admin')
def user_management(request):
    """إدارة المستخدمين"""
    from accounts.models import CustomUser
    
    users = CustomUser.objects.all().order_by('-date_joined')
    
    # التصفية حسب النوع
    user_type = request.GET.get('type', 'all')
    if user_type != 'all':
        users = users.filter(user_type=user_type)
    
    # البحث
    query = request.GET.get('q')
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        )
    
    # الترقيم
    paginator = Paginator(users, 30)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'users': page_obj,
        'user_type': user_type,
        'query': query,
    }
    
    return render(request, 'dashboard/users.html', context)

@login_required
@user_passes_test(lambda u: u.user_type == 'admin')
def edit_user(request, pk):
    """تعديل بيانات المستخدم"""
    from accounts.models import CustomUser
    from accounts.forms import AdminUserForm
    
    user = get_object_or_404(CustomUser, pk=pk)
    
    if request.method == 'POST':
        form = AdminUserForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, _('User updated successfully'))
            return redirect('dashboard:users')
    else:
        form = AdminUserForm(instance=user)
    
    context = {
        'form': form,
        'user': user,
    }
    
    return render(request, 'dashboard/edit_user.html', context)

@login_required
@user_passes_test(lambda u: u.user_type == 'admin')
def site_settings(request):
    """إعدادات الموقع"""
    from core.models import SiteSetting
    
    settings_obj, created = SiteSetting.objects.get_or_create(pk=1)
    
    if request.method == 'POST':
        from core.forms import SiteSettingForm
        form = SiteSettingForm(request.POST, request.FILES, instance=settings_obj)
        if form.is_valid():
            form.save()
            messages.success(request, _('Site settings updated successfully'))
            return redirect('dashboard:settings')
    else:
        from core.forms import SiteSettingForm
        form = SiteSettingForm(instance=settings_obj)
    
    context = {
        'form': form,
    }
    
    return render(request, 'dashboard/settings.html', context)

@login_required
@user_passes_test(lambda u: u.user_type == 'admin')
def analytics(request):
    """التحليلات والإحصائيات"""
    from django.db.models import Count, Avg
    from django.utils import timezone
    from datetime import timedelta
    
    # حساب الفترات الزمنية
    today = timezone.now().date()
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)
    
    # إحصائيات المحتوى
    from articles.models import Article
    from courses.models import Course, Enrollment
    from books.models import Book
    from scholarships.models import Scholarship
    
    content_stats = {
        'total_articles': Article.objects.count(),
        'total_courses': Course.objects.count(),
        'total_books': Book.objects.count(),
        'total_scholarships': Scholarship.objects.count(),
        'recent_articles': Article.objects.filter(created_at__gte=last_week).count(),
        'recent_courses': Course.objects.filter(created_at__gte=last_week).count(),
    }
    
    # إحصائيات المستخدمين
    from accounts.models import CustomUser
    
    user_stats = {
        'total_users': CustomUser.objects.count(),
        'new_users_week': CustomUser.objects.filter(date_joined__gte=last_week).count(),
        'new_users_month': CustomUser.objects.filter(date_joined__gte=last_month).count(),
        'admins': CustomUser.objects.filter(user_type='admin').count(),
        'editors': CustomUser.objects.filter(user_type='editor').count(),
        'regular_users': CustomUser.objects.filter(user_type='user').count(),
    }
    
    # إحصائيات التفاعل
    interaction_stats = {
        'total_enrollments': Enrollment.objects.count(),
        'recent_enrollments': Enrollment.objects.filter(enrolled_at__gte=last_week).count(),
        'average_course_rating': Course.objects.aggregate(
            avg=Avg('reviews__rating')
        )['avg'] or 0,
    }
    
    # الرسوم البيانية (بيانات وهمية للمثال)
    monthly_data = [
        {'month': 'Jan', 'users': 150, 'enrollments': 45},
        {'month': 'Feb', 'users': 220, 'enrollments': 68},
        {'month': 'Mar', 'users': 310, 'enrollments': 92},
        {'month': 'Apr', 'users': 280, 'enrollments': 85},
        {'month': 'May', 'users': 350, 'enrollments': 110},
        {'month': 'Jun', 'users': 420, 'enrollments': 135},
    ]
    
    content_distribution = [
        {'type': 'Articles', 'count': content_stats['total_articles']},
        {'type': 'Courses', 'count': content_stats['total_courses']},
        {'type': 'Books', 'count': content_stats['total_books']},
        {'type': 'Scholarships', 'count': content_stats['total_scholarships']},
    ]
    
    context = {
        'content_stats': content_stats,
        'user_stats': user_stats,
        'interaction_stats': interaction_stats,
        'monthly_data': monthly_data,
        'content_distribution': content_distribution,
    }
    
    return render(request, 'dashboard/analytics.html', context)