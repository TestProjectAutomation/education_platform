from django.shortcuts import render
from django.db.models import Count
from django.utils.translation import gettext_lazy as _
from articles.models import Article
from books.models import Book
from blog.models import Post, Category

def home(request):    
    # المقالات المميزة
    featured_articles = Article.objects.filter(
        status='published',
        is_featured=True
    ).order_by('-created_at')[:4]
    
    categorys_hed = Category.objects.all()


    # الكتب المميزة
    featured_books = Book.objects.filter(
        status='published',
        is_featured=True
    ).order_by('-created_at')[:4]
    
    # الإحصائيات
    stats = {
        'total_articles': Article.objects.filter(status='published').count(),
        'total_books': Book.objects.filter(status='published').count(),
        'total_students': 1250,  # في التطبيق الحقيقي، سيتم حسابها من قاعدة البيانات
    }
    stats_fallback = {
        "total_courses": 150,
        "total_students": 4500,
        "total_articles": 250,
        "total_scholarships": 80,
        "total_books": 120,
    }

    context = {
        'featured_articles': featured_articles,
        'featured_books': featured_books,
        'stats': stats,
        'stats_fallback': stats_fallback,
        'categorys_hed': categorys_hed
    }
    
    return render(request, 'core/home.html', context)

def about(request):
    """صفحة من نحن"""
    return render(request, 'core/about.html')

def contact(request):
    """صفحة اتصل بنا"""
    if request.method == 'POST':
        # معالجة نموذج الاتصال
        pass
    
    return render(request, 'core/contact.html')

def search(request):
    """صفحة البحث المتقدم"""
    query = request.GET.get('q', '')
    search_type = request.GET.get('type', 'all')
    
    results = []
    
    if query:
        if search_type in ['all', 'courses']:
            courses = Course.objects.filter(
                status='published',
                title__icontains=query
            )[:5]
            results.append({
                'type': 'courses',
                'title': _('Courses'),
                'items': courses,
                'count': courses.count(),
            })
        
        if search_type in ['all', 'articles']:
            articles = Article.objects.filter(
                status='published',
                title__icontains=query
            )[:5]
            results.append({
                'type': 'articles',
                'title': _('Articles'),
                'items': articles,
                'count': articles.count(),
            })
        
        if search_type in ['all', 'books']:
            books = Book.objects.filter(
                status='published',
                title__icontains=query
            )[:5]
            results.append({
                'type': 'books',
                'title': _('Books'),
                'items': books,
                'count': books.count(),
            })
        
        if search_type in ['all', 'scholarships']:
            scholarships = Scholarship.objects.filter(
                status='published',
                title__icontains=query
            )[:5]
            results.append({
                'type': 'scholarships',
                'title': _('Scholarships'),
                'items': scholarships,
                'count': scholarships.count(),
            })
    
    context = {
        'query': query,
        'search_type': search_type,
        'results': results,
        'has_results': any(r['count'] > 0 for r in results),
    }
    
    return render(request, 'core/search.html', context)

def privacy_policy(request):
    """سياسة الخصوصية"""
    return render(request, 'core/privacy.html')

def terms_of_service(request):
    """شروط الخدمة"""
    return render(request, 'core/terms.html')