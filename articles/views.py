from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .models import Article, Tag, Comment
# from .forms import CommentForm

def article_list(request):
    """عرض قائمة المقالات"""
    articles = Article.objects.filter(status='published').order_by('-created_at')
    
    # البحث والتصفية
    query = request.GET.get('q')
    tag = request.GET.get('tag')
    category = request.GET.get('category')
    
    if query:
        articles = articles.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query)
        )
    
    if tag:
        articles = articles.filter(tags__slug=tag)
    
    if category:
        articles = articles.filter(categories__slug=category)
    
    # المقالات المميزة
    featured_articles = articles.filter(is_featured=True)[:3]
    
    # الوسوم الشائعة
    popular_tags = Tag.objects.annotate(
        article_count=Count('article')
    ).order_by('-article_count')[:10]
    
    # الترقيم
    paginator = Paginator(articles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'articles': page_obj,
        'featured_articles': featured_articles,
        'popular_tags': popular_tags,
        'query': query,
        'tag': tag,
        'category': category,
    }
    
    return render(request, 'articles/list.html', context)

def article_detail(request, slug):
    """عرض تفاصيل المقال"""
    article = get_object_or_404(Article, slug=slug, status='published')
    
    # زيادة عدد المشاهدات
    article.increment_views()
    
    # المقالات المشابهة
    related_articles = Article.objects.filter(
        categories__in=article.categories.all(),
        status='published'
    ).exclude(id=article.id).distinct()[:3]
    
    # التعليقات
    comments = article.comments.filter(is_approved=True).order_by('-created_at')
    
    # إضافة تعليق
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.save()
            
            messages.success(request, _('Your comment has been submitted and is awaiting moderation'))
            return redirect('articles:detail', slug=slug)
    else:
        form = CommentForm()
    
    context = {
        'article': article,
        'related_articles': related_articles,
        'comments': comments,
        'form': form,
    }
    
    return render(request, 'articles/detail.html', context)

def article_by_tag(request, slug):
    """عرض المقالات حسب الوسم"""
    tag = get_object_or_404(Tag, slug=slug)
    articles = Article.objects.filter(
        tags=tag,
        status='published'
    ).order_by('-created_at')
    
    # الترقيم
    paginator = Paginator(articles, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'tag': tag,
        'articles': page_obj,
    }
    
    return render(request, 'articles/tag.html', context)