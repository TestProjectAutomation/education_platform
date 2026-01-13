from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse, HttpResponse, HttpResponseForbidden
from django.db.models import Sum, Count, Q, F, Avg, Max, Min
from django.utils import timezone
from django.core.cache import cache
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.cache import cache_page
from django.contrib.syndication.views import Feed
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from datetime import datetime, timedelta
import json
import csv
from .models import *
from advertisements.models import Advertisement, AdPlacement
from advertisements.utils import generate_ad_code
from .forms import ArticleForm, CommentForm, ArticleFilterForm
from .decorators import premium_required, track_article_view

# ==============================================
# وظائف العرض الرئيسية
# ==============================================

@cache_page(60 * 15)  # كاش لمدة 15 دقيقة
def article_list(request):
    """قائمة جميع المقالات مع خيارات التصفية المتقدمة"""
    # الحصول على معاملات البحث والتصفية
    form = ArticleFilterForm(request.GET or None)
    
    # البدء بجميع المقالات المنشورة
    articles = Article.objects.filter(status='published')
    
    if form.is_valid():
        # تطبيق الفلاتر
        category = form.cleaned_data.get('category')
        tags = form.cleaned_data.get('tags')
        author = form.cleaned_data.get('author')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        search_query = form.cleaned_data.get('search')
        sort_by = form.cleaned_data.get('sort_by', '-published_at')
        show_featured = form.cleaned_data.get('show_featured')
        show_premium = form.cleaned_data.get('show_premium')
        
        # تطبيق الفلاتر
        if category:
            articles = articles.filter(category=category)
        
        if tags:
            articles = articles.filter(tags__in=tags).distinct()
        
        if author:
            articles = articles.filter(author=author)
        
        if date_from:
            articles = articles.filter(published_at__gte=date_from)
        
        if date_to:
            articles = articles.filter(published_at__lte=date_to)
        
        if search_query:
            articles = articles.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(excerpt__icontains=search_query) |
                Q(tags__name__icontains=search_query) |
                Q(category__name__icontains=search_query) |
                Q(author__username__icontains=search_query)
            ).distinct()
        
        if not show_featured:
            articles = articles.filter(is_featured=False)
        
        if not show_premium and not request.user.is_authenticated:
            articles = articles.filter(is_premium=False)
        
        # الترتيب
        if sort_by == 'views':
            articles = articles.order_by('-views')
        elif sort_by == 'title':
            articles = articles.order_by('title')
        elif sort_by == '-title':
            articles = articles.order_by('-title')
        elif sort_by == 'rating':
            articles = articles.annotate(
                avg_rating=Avg('ratings__rating')
            ).order_by('-avg_rating')
        elif sort_by == 'comments':
            articles = articles.annotate(
                comments_count=Count('comments', filter=Q(comments__is_approved=True))
            ).order_by('-comments_count')
        else:  # الافتراضي: الأحدث أولاً
            articles = articles.order_by('-is_pinned', '-published_at')
    else:
        # الافتراضي: المقالات المنشورة غير المميزة (لغير المسجلين)
        articles = articles.order_by('-is_pinned', '-published_at')
        if not request.user.is_authenticated:
            articles = articles.filter(is_premium=False)
    
    # الترقيم
    paginator = Paginator(articles, 18)  # 18 مقالة في الصفحة
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # الحصول على الإعلانات الجانبية
    sidebar_ads = Advertisement.objects.filter(
        active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now(),
        placement__code='sidebar'
    ).order_by('-priority', '?')[:2]
    
    # التحضير للإعلانات
    sidebar_ads_display = []
    for ad in sidebar_ads:
        sidebar_ads_display.append({
            'html': generate_ad_code(ad.ad_type, ad.get_content_for_api(), ad.link, ad.id),
            'width': ad.placement.width if ad.placement else 300,
        })
    
    # إحصائيات
    stats = {
        'total_articles': Article.objects.filter(status='published').count(),
        'total_categories': Category.objects.filter(is_active=True).count(),
        'total_tags': Tag.objects.count(),
        'total_views': Article.objects.filter(status='published').aggregate(Sum('views'))['views__sum'] or 0,
        'featured_count': Article.objects.filter(status='published', is_featured=True).count(),
    }
    
    # الحصول على التصنيفات والوسوم الشائعة
    popular_categories = Category.objects.filter(
        is_active=True,
        articles__status='published'
    ).annotate(
        articles_count=Count('articles', filter=Q(articles__status='published'))
    ).order_by('-articles_count')[:10]
    
    popular_tags = Tag.objects.annotate(
        articles_count=Count('article', filter=Q(article__status='published'))
    ).order_by('-articles_count')[:20]
    
    context = {
        'articles': page_obj,
        'form': form,
        'sidebar_ads': sidebar_ads_display,
        'stats': stats,
        'popular_categories': popular_categories,
        'popular_tags': popular_tags,
        'page_title': _('Articles'),
        'meta_description': _('Browse our comprehensive library of articles on various topics'),
    }
    
    return render(request, 'articles/list.html', context)

@cache_page(60 * 5)  # كاش لمدة 5 دقائق
def article_by_tag(request, slug):
    """عرض المقالات حسب الوسم مع عرض الإعلانات المناسبة"""
    # الحصول على الوسم
    tag = get_object_or_404(Tag, slug=slug)
    
    # زيادة عدد المشاهدات للوسم
    tag.views += 1
    tag.save(update_fields=['views'])
    
    # الحصول على المقالات المنشورة بهذا الوسم
    articles = Article.objects.filter(
        tags=tag,
        status='published'
    ).select_related('author', 'category').prefetch_related('tags').order_by('-published_at')
    
    # الترقيم
    paginator = Paginator(articles, 12)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # الحصول على الإعلانات المناسبة لهذا الوسم
    relevant_ads = Advertisement.objects.filter(
        active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now(),
    ).filter(
        Q(tags__slug=slug) | Q(tags__isnull=True)
    ).distinct().order_by('-priority', '?')[:3]
    
    # إذا لم يكن هناك إعلانات خاصة بهذا الوسم، نأخذ إعلانات عامة
    if not relevant_ads.exists():
        relevant_ads = Advertisement.objects.filter(
            active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now(),
            tags__isnull=True
        ).order_by('-priority', '?')[:3]
    
    # إحصائيات الوسم
    tag_stats = {
        'total_articles': articles.count(),
        'latest_article': articles.first(),
        'most_viewed': articles.order_by('-views').first() if articles.exists() else None,
        'avg_reading_time': articles.aggregate(Avg('reading_time'))['reading_time__avg'] or 0,
        'total_views': articles.aggregate(Sum('views'))['views__sum'] or 0,
    }
    
    # الوسوم ذات الصلة
    related_tags = Tag.objects.filter(
        article__in=articles
    ).exclude(id=tag.id).annotate(
        article_count=Count('article')
    ).order_by('-article_count')[:10]
    
    # تحضير بيانات الإعلانات للعرض
    ads_display = []
    for ad in relevant_ads:
        ad_data = {
            'id': ad.id,
            'title': ad.title,
            'type': ad.ad_type,
            'content': ad.get_content_for_api(),
            'link': ad.link,
            'placement': ad.placement.code if ad.placement else 'general',
            'html': generate_ad_code(ad.ad_type, ad.get_content_for_api(), ad.link, ad.id),
            'width': ad.placement.width if ad.placement else 300,
            'height': ad.placement.height if ad.placement else 250,
        }
        ads_display.append(ad_data)
    
    # المقالات المميزة في هذا الوسم
    featured_in_tag = articles.filter(is_featured=True)[:3]
    
    context = {
        'tag': tag,
        'articles': page_obj,
        'ads': ads_display,
        'tag_stats': tag_stats,
        'related_tags': related_tags,
        'featured_in_tag': featured_in_tag,
        'page_title': _('Articles tagged with "{tag}"').format(tag=tag.name),
        'meta_description': tag.description[:160] if tag.description else 
                           _('Browse all articles published under the tag {tag}').format(tag=tag.name),
        'breadcrumbs': [
            {'name': _('Home'), 'url': '/'},
            {'name': _('Articles'), 'url': reverse('articles:list')},
            {'name': _('Tag: {tag}').format(tag=tag.name), 'url': ''},
        ],
    }
    
    return render(request, 'articles/tag.html', context)

@cache_page(60 * 5)
def article_by_category(request, slug):
    """عرض المقالات حسب التصنيف"""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    
    # الحصول على المقالات في هذا التصنيف
    articles = Article.objects.filter(
        category=category,
        status='published'
    ).order_by('-is_pinned', '-published_at')
    
    # الترقيم
    paginator = Paginator(articles, 12)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # الإعلانات
    category_ads = Advertisement.objects.filter(
        active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now(),
        placement__code='sidebar'
    ).order_by('-priority', '?')[:2]
    
    # الأقسام الفرعية
    subcategories = category.children.filter(is_active=True)
    
    context = {
        'category': category,
        'articles': page_obj,
        'subcategories': subcategories,
        'ads': [generate_ad_code(ad.ad_type, ad.get_content_for_api(), ad.link, ad.id) for ad in category_ads],
        'page_title': _('Articles in {category}').format(category=category.name),
        'meta_description': category.description[:160] if category.description else 
                           _('Browse articles in the {category} category').format(category=category.name),
    }
    
    return render(request, 'articles/category.html', context)

@track_article_view
def article_detail(request, slug):
    """عرض مقال مفصل"""
    article = get_object_or_404(
        Article.objects.select_related('author', 'category')
        .prefetch_related('tags'),
        slug=slug
    )
    
    # التحقق من حالة المقال
    if article.status != 'published':
        if not request.user.is_staff:
            raise Http404(_("This article is not published."))
    
    # التحقق من المحتوى المميز
    if article.is_premium and not request.user.is_authenticated:
        messages.info(request, _('This is a premium article. Please login to access.'))
        return redirect(f'{reverse("account_login")}?next={request.path}')
    
    # زيادة المشاهدات
    article.increment_views()
    
    # الحصول على المقالات ذات الصلة
    related_articles = article.get_related_articles_with_fallback(3)
    
    # التعليقات المعتمدة
    comments = article.comments.filter(
        is_approved=True,
        is_spam=False,
        parent__isnull=True
    ).select_related('user').prefetch_related('replies')
    
    # الحصول على الإعلانات
    ads = get_article_ads(article)
    
    # تقسيم المحتوى للإعلانات
    content_with_ads = insert_ads_in_content(article.content, ads.get('in_content', []))
    
    # تقييم المستخدم إذا كان مسجلاً
    user_rating = None
    if request.user.is_authenticated:
        user_rating = ArticleRating.objects.filter(
            article=article,
            user=request.user
        ).first()
    
    # التحقق من الإشارات المرجعية
    is_bookmarked = False
    if request.user.is_authenticated:
        is_bookmarked = Bookmark.objects.filter(
            user=request.user,
            article=article
        ).exists()
    
    context = {
        'article': article,
        'content_with_ads': content_with_ads,
        'related_articles': related_articles,
        'comments': comments,
        'comment_form': CommentForm(),
        'ads': ads,
        'user_rating': user_rating.rating if user_rating else None,
        'is_bookmarked': is_bookmarked,
        'share_url': request.build_absolute_uri(article.get_absolute_url()),
        'page_title': article.meta_title or article.title,
        'meta_description': article.meta_description or article.excerpt[:160],
        'meta_keywords': ', '.join([tag.name for tag in article.tags.all()]),
        'breadcrumbs': [
            {'name': _('Home'), 'url': '/'},
            {'name': _('Articles'), 'url': reverse('articles:list')},
            {'name': article.category.name if article.category else _('Uncategorized'), 
             'url': article.category.get_absolute_url() if article.category else '#'},
            {'name': article.title, 'url': ''},
        ],
    }
    
    return render(request, 'articles/detail.html', context)

# ==============================================
# وظائف البحث والتصفية
# ==============================================

def article_search(request):
    """بحث متقدم في المقالات"""
    query = request.GET.get('q', '')
    
    if not query:
        return redirect('articles:list')
    
    # البحث في مختلف الحقول
    articles = Article.objects.filter(
        Q(title__icontains=query) |
        Q(content__icontains=query) |
        Q(excerpt__icontains=query) |
        Q(tags__name__icontains=query) |
        Q(category__name__icontains=query) |
        Q(author__username__icontains=query),
        status='published'
    ).distinct().order_by('-published_at')
    
    # الترقيم
    paginator = Paginator(articles, 12)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # الإعلانات
    search_ads = Advertisement.objects.filter(
        active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now(),
        placement__code='sidebar'
    ).order_by('-priority', '?')[:2]
    
    context = {
        'articles': page_obj,
        'query': query,
        'results_count': articles.count(),
        'ads': [generate_ad_code(ad.ad_type, ad.get_content_for_api(), ad.link, ad.id) for ad in search_ads],
        'page_title': _('Search results for "{query}"').format(query=query),
        'meta_description': _('Search results for {query}').format(query=query),
    }
    
    return render(request, 'articles/search.html', context)

def article_archive(request):
    """أرشيف المقالات حسب التاريخ"""
    # الحصول على السنوات التي بها مقالات
    years = Article.objects.filter(
        status='published',
        published_at__isnull=False
    ).dates('published_at', 'year', order='DESC')
    
    selected_year = request.GET.get('year')
    selected_month = request.GET.get('month')
    
    articles = Article.objects.filter(status='published')
    
    if selected_year:
        articles = articles.filter(published_at__year=selected_year)
    
    if selected_month:
        articles = articles.filter(published_at__month=selected_month)
    
    # الترقيم
    paginator = Paginator(articles, 24)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    # تنظيم الأرشيف حسب الشهور
    archive_data = {}
    for year in years:
        months = Article.objects.filter(
            status='published',
            published_at__year=year.year
        ).dates('published_at', 'month', order='DESC')
        
        month_data = []
        for month in months:
            count = Article.objects.filter(
                status='published',
                published_at__year=year.year,
                published_at__month=month.month
            ).count()
            
            month_data.append({
                'month': month,
                'count': count,
                'month_name': month.strftime('%B')
            })
        
        archive_data[year.year] = {
            'year': year,
            'months': month_data,
            'count': Article.objects.filter(
                status='published',
                published_at__year=year.year
            ).count()
        }
    
    context = {
        'articles': page_obj,
        'archive_data': archive_data,
        'selected_year': int(selected_year) if selected_year else None,
        'selected_month': int(selected_month) if selected_month else None,
        'page_title': _('Article Archive'),
        'meta_description': _('Browse articles by publication date'),
    }
    
    return render(request, 'articles/archive.html', context)

# ==============================================
# المقالات المميزة والشائعة
# ==============================================

def featured_articles(request):
    """المقالات المميزة"""
    articles = Article.objects.filter(
        status='published',
        is_featured=True
    ).order_by('-published_at')
    
    paginator = Paginator(articles, 12)
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'articles': page_obj,
        'page_title': _('Featured Articles'),
        'meta_description': _('Our top featured articles on various topics'),
    }
    
    return render(request, 'articles/featured.html', context)

def popular_articles(request):
    """المقالات الشائعة"""
    # المقالات الأكثر مشاهدة في آخر 30 يوم
    cutoff_date = timezone.now() - timedelta(days=30)
    
    articles = Article.objects.filter(
        status='published',
        published_at__gte=cutoff_date
    ).order_by('-views')[:50]
    
    context = {
        'articles': articles,
        'page_title': _('Popular Articles'),
        'meta_description': _('Most viewed articles in the last 30 days'),
    }
    
    return render(request, 'articles/popular.html', context)

def latest_articles(request):
    """أحدث المقالات"""
    articles = Article.objects.filter(
        status='published'
    ).order_by('-published_at')[:50]
    
    context = {
        'articles': articles,
        'page_title': _('Latest Articles'),
        'meta_description': _('Our most recently published articles'),
    }
    
    return render(request, 'articles/latest.html', context)

# ==============================================
# التفاعلات مع المقالات
# ==============================================

@require_POST
def rate_article(request, slug):
    """تقييم مقال"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': _('Authentication required')}, status=401)
    
    article = get_object_or_404(Article, slug=slug, status='published')
    rating = request.POST.get('rating')
    
    try:
        rating = int(rating)
        if rating < 1 or rating > 5:
            raise ValueError
    except (ValueError, TypeError):
        return JsonResponse({'error': _('Invalid rating')}, status=400)
    
    # التحقق من عدم التقييم مسبقاً
    existing_rating = ArticleRating.objects.filter(
        article=article,
        user=request.user
    ).first()
    
    if existing_rating:
        existing_rating.rating = rating
        existing_rating.save()
        message = _('Rating updated')
    else:
        ArticleRating.objects.create(
            article=article,
            user=request.user,
            rating=rating,
            ip_address=request.META.get('REMOTE_ADDR')
        )
        message = _('Rating submitted')
    
    # حساب المعدل الجديد
    avg_rating = article.ratings.aggregate(Avg('rating'))['rating__avg'] or 0
    
    return JsonResponse({
        'success': True,
        'message': message,
        'avg_rating': round(avg_rating, 1),
        'rating_count': article.ratings.count()
    })

@require_POST
@login_required
def bookmark_article(request, slug):
    """إضافة/إزالة مقال من المفضلة"""
    article = get_object_or_404(Article, slug=slug, status='published')
    
    bookmark, created = Bookmark.objects.get_or_create(
        user=request.user,
        article=article
    )
    
    if not created:
        bookmark.delete()
        action = 'removed'
    else:
        action = 'added'
    
    return JsonResponse({
        'success': True,
        'action': action,
        'bookmarks_count': request.user.bookmarks.count()
    })

@require_POST
def add_comment(request, slug):
    """إضافة تعليق على مقال"""
    article = get_object_or_404(Article, slug=slug, status='published')
    
    if not article.allow_comments:
        return JsonResponse({'error': _('Comments are disabled for this article')}, status=403)
    
    form = CommentForm(request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.article = article
        comment.ip_address = request.META.get('REMOTE_ADDR')
        comment.user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        if request.user.is_authenticated:
            comment.user = request.user
            comment.name = request.user.get_full_name() or request.user.username
            comment.email = request.user.email
        
        # اعتماد تلقائي للتعليقات من المستخدمين المسجلين
        if request.user.is_authenticated and request.user.has_perm('articles.can_approve_comments'):
            comment.is_approved = True
        
        comment.save()
        
        # إرسال إشعار للمسؤول
        send_comment_notification(comment)
        
        messages.success(request, _('Your comment has been submitted and is awaiting approval.'))
    else:
        messages.error(request, _('Please correct the errors in the comment form.'))
    
    return redirect('articles:detail', slug=slug)

@require_POST
@login_required
def add_reply(request, pk):
    """إضافة رد على تعليق"""
    parent_comment = get_object_or_404(Comment, pk=pk, is_approved=True)
    
    if not parent_comment.article.allow_comments:
        return JsonResponse({'error': _('Comments are disabled for this article')}, status=403)
    
    form = CommentForm(request.POST)
    
    if form.is_valid():
        reply = form.save(commit=False)
        reply.article = parent_comment.article
        reply.parent = parent_comment
        reply.ip_address = request.META.get('REMOTE_ADDR')
        reply.user_agent = request.META.get('HTTP_USER_AGENT', '')
        reply.user = request.user
        reply.name = request.user.get_full_name() or request.user.username
        reply.email = request.user.email
        
        # اعتماد تلقائي للردود من المستخدمين المسجلين
        if request.user.has_perm('articles.can_approve_comments'):
            reply.is_approved = True
        
        reply.save()
        
        messages.success(request, _('Your reply has been submitted.'))
    else:
        messages.error(request, _('Please correct the errors in your reply.'))
    
    return redirect('articles:detail', slug=parent_comment.article.slug)

@require_POST
def vote_comment(request, pk):
    """التصويت على تعليق"""
    comment = get_object_or_404(Comment, pk=pk, is_approved=True)
    vote_type = request.POST.get('type')  # 'like' or 'dislike'
    
    # استخدام الجلسة لمنع التصويت المتكرر
    session_key = f'comment_vote_{pk}'
    if request.session.get(session_key):
        return JsonResponse({'error': _('You have already voted on this comment')}, status=400)
    
    if vote_type == 'like':
        comment.likes += 1
    elif vote_type == 'dislike':
        comment.dislikes += 1
    else:
        return JsonResponse({'error': _('Invalid vote type')}, status=400)
    
    comment.save()
    
    # حفظ في الجلسة
    request.session[session_key] = True
    
    return JsonResponse({
        'success': True,
        'likes': comment.likes,
        'dislikes': comment.dislikes,
        'score': comment.get_vote_score()
    })

# ==============================================
# وظائف خدمية
# ==============================================

def get_article_ads(article):
    """الحصول على الإعلانات المناسبة للمقال"""
    ads = {
        'top': None,
        'sidebar': [],
        'in_content': [],
        'bottom': None
    }
    
    # إعلان في الأعلى
    top_ad = Advertisement.objects.filter(
        active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now(),
        placement__code='header',
        tags__in=article.tags.all()
    ).order_by('-priority', '?').first()
    
    if top_ad:
        ads['top'] = generate_ad_code(top_ad.ad_type, top_ad.get_content_for_api(), top_ad.link, top_ad.id)
    
    # إعلانات في الجانب
    sidebar_ads = Advertisement.objects.filter(
        active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now(),
        placement__code='sidebar'
    ).order_by('-priority', '?')[:2]
    
    for ad in sidebar_ads:
        ads['sidebar'].append(generate_ad_code(ad.ad_type, ad.get_content_for_api(), ad.link, ad.id))
    
    # إعلانات داخل المحتوى
    in_content_ads = Advertisement.objects.filter(
        active=True,
        start_date__lte=timezone.now(),
        end_date__gte=timezone.now(),
        placement__code='in_content'
    ).order_by('-priority', '?')[:2]
    
    for ad in in_content_ads:
        ads['in_content'].append({
            'html': generate_ad_code(ad.ad_type, ad.get_content_for_api(), ad.link, ad.id),
            'position': None  # سيتم تحديده تلقائياً
        })
    
    return ads

def insert_ads_in_content(content, ads):
    """إدراج الإعلانات داخل المحتوى"""
    if not ads:
        return content
    
    paragraphs = content.split('\n\n')
    total_paragraphs = len(paragraphs)
    
    # لا ندرج إعلانات إذا كان المحتوى قصيراً
    if total_paragraphs < 5:
        return content
    
    # تحديد أماكن الإعلانات
    ad_positions = []
    
    # أول إعلان بعد الفقرة الثانية
    if total_paragraphs > 3:
        ad_positions.append(2)
    
    # إعلان ثاني قبل الفقرة قبل الأخيرة
    if total_paragraphs > 7:
        ad_positions.append(total_paragraphs - 2)
    
    # إدراج الإعلانات
    result_paragraphs = []
    ad_index = 0
    
    for i, paragraph in enumerate(paragraphs):
        result_paragraphs.append(paragraph)
        
        if i in ad_positions and ad_index < len(ads):
            result_paragraphs.append(
                f'<div class="in-content-ad ad-position-{ad_index + 1}">'
                f'{ads[ad_index]["html"]}'
                f'</div>'
            )
            ad_index += 1
    
    return '\n\n'.join(result_paragraphs)

def send_article_by_email(article, recipient_email, sender_user):
    """إرسال المقال عبر البريد الإلكتروني"""
    subject = _('Article shared with you: {article}').format(article=article.title)
        
    context = {
        'article': article,
        'sender': sender_user,
        'article_url': article.get_absolute_url(),
    }
    
    message = render_to_string('emails/share_article.html', context)
    
    send_mail(
        subject,
        message,
        'noreply@example.com',
        [recipient_email],
        html_message=message,
        fail_silently=True
    )

def send_comment_notification(request ,comment):
    """إرسال إشعار بالتعليق الجديد"""
    subject = _('New comment on article: {article}').format(article=comment.article.title)
    
    context = {
        'comment': comment,
        'article': comment.article,
        'admin_url': request.build_absolute_uri(reverse('admin:articles_comment_change', args=[comment.id]))
    }
    
    message = render_to_string('emails/new_comment_notification.html', context)
    
    # إرسال للمسؤولين
    from django.contrib.auth.models import User
    admin_emails = User.objects.filter(
        is_staff=True,
        email__isnull=False
    ).values_list('email', flat=True)
    
    if admin_emails:
        send_mail(
            subject,
            message,
            'noreply@example.com',
            list(admin_emails),
            html_message=message,
            fail_silently=True
        )

def print_article(request, slug):
    """عرض المقال للطباعة"""
    article = get_object_or_404(Article, slug=slug, status='published')
    
    context = {
        'article': article,
        'print_mode': True,
    }
    
    return render(request, 'articles/print.html', context)

def share_article(request, slug):
    """مشاركة المقال"""
    article = get_object_or_404(Article, slug=slug, status='published')
    
    if request.method == 'POST':
        share_method = request.POST.get('method')
        email = request.POST.get('email', '')
        
        if share_method == 'email' and email:
            # إرسال بالبريد الإلكتروني
            send_article_by_email(article, email, request.user)
            messages.success(request, _('Article shared successfully by email.'))
        elif share_method in ['facebook', 'twitter', 'linkedin']:
            # روابط المشاركة الاجتماعية
            return JsonResponse({
                'success': True,
                'share_url': get_social_share_url(article, share_method, request)
            })
    
    return redirect('articles:detail', slug=slug)

# ==============================================
# التقارير والإحصائيات
# ==============================================

@login_required
@user_passes_test(lambda u: u.is_staff)
def article_statistics(request):
    """إحصائيات المقالات"""
    # إحصائيات عامة
    stats = {
        'total_articles': Article.objects.count(),
        'published_articles': Article.objects.filter(status='published').count(),
        'draft_articles': Article.objects.filter(status='draft').count(),
        'total_views': Article.objects.aggregate(Sum('views'))['views__sum'] or 0,
        'total_comments': Comment.objects.filter(is_approved=True).count(),
        'avg_reading_time': Article.objects.filter(status='published').aggregate(Avg('reading_time'))['reading_time__avg'] or 0,
    }
    
    # المقالات الأكثر مشاهدة
    most_viewed = Article.objects.filter(status='published').order_by('-views')[:10]
    
    # المقالات الأكثر تعليقاً
    most_commented = Article.objects.filter(status='published').annotate(
        comments_count=Count('comments', filter=Q(comments__is_approved=True))
    ).order_by('-comments_count')[:10]
    
    # التوزيع حسب التصنيف
    by_category = Category.objects.annotate(
        articles_count=Count('articles', filter=Q(articles__status='published')),
        total_views=Sum('articles__views', filter=Q(articles__status='published'))
    ).order_by('-articles_count')
    
    # التوزيع حسب الشهر
    from django.db.models.functions import TruncMonth
    by_month = Article.objects.filter(
        status='published',
        published_at__isnull=False
    ).annotate(
        month=TruncMonth('published_at')
    ).values('month').annotate(
        count=Count('id'),
        views=Sum('views')
    ).order_by('-month')
    
    context = {
        'stats': stats,
        'most_viewed': most_viewed,
        'most_commented': most_commented,
        'by_category': by_category,
        'by_month': by_month,
        'page_title': _('Article Statistics'),
    }
    
    return render(request, 'articles/statistics.html', context)

def article_sitemap(request):
    """خريطة الموقع للمقالات"""
    articles = Article.objects.filter(
        status='published',
        published_at__isnull=False
    ).order_by('-published_at')
    
    context = {
        'articles': articles,
        'base_url': request.build_absolute_uri('/')[:-1]
    }
    
    response = render(request, 'articles/sitemap.xml', context)
    response['Content-Type'] = 'application/xml'
    
    return response

def article_rss_feed(request):
    """تغذية RSS للمقالات"""
    articles = Article.objects.filter(
        status='published',
        published_at__isnull=False
    ).order_by('-published_at')[:20]
    
    context = {
        'articles': articles,
        'site_url': request.build_absolute_uri('/')[:-1],
        'feed_url': request.build_absolute_uri(),
    }
    
    response = render(request, 'articles/rss_feed.xml', context)
    response['Content-Type'] = 'application/rss+xml'
    
    return response

# ==============================================
# الديكورات المساعدة
# ==============================================

def premium_required(view_func):
    """طلب الاشتراك المميز للوصول للمقال"""
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.has_perm('articles.can_view_premium'):
            return view_func(request, *args, **kwargs)
        else:
            messages.info(request, _('This content requires a premium subscription.'))
            return redirect('subscription:plans')
    return wrapper

def track_article_view(view_func):
    """تتبع مشاهدات المقال"""
    def wrapper(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        
        if request.method == 'GET' and hasattr(response, 'context_data'):
            article = response.context_data.get('article')
            if article and isinstance(article, Article):
                # تسجيل المشاهدة
                ArticleView.objects.create(
                    article=article,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', ''),
                    session_key=request.session.session_key or 'anonymous'
                )
        
        return response
    return wrapper
