from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Post, Category

def post_list(request):
    posts = Post.objects.filter(status=Post.Status.PUBLISHED).order_by('-publish_date')
    
    # Pagination
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'posts': page_obj,
        'page_obj': page_obj,
    }
    
    return render(request, 'blog/post_list.html', context)

def post_detail(request, slug):
    post = get_object_or_404(Post, slug=slug, status=Post.Status.PUBLISHED)
    
    # Increase views
    post.increase_views()
    
    # Related posts
    related_posts = post.get_related_posts()
    
    context = {
        'post': post,
        'related_posts': related_posts,
    }
    
    return render(request, 'blog/post_detail.html', context)

def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug, is_active=True)
    posts = Post.objects.filter(
        category=category,
        status=Post.Status.PUBLISHED
    ).order_by('-publish_date')
    
    # Pagination
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'posts': page_obj,
        'page_obj': page_obj,
    }
    
    return render(request, 'blog/category_detail.html', context)

def search(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    
    posts = Post.objects.filter(status=Post.Status.PUBLISHED)
    
    if query:
        posts = posts.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query)
        )
    
    if category:
        posts = posts.filter(category__slug=category)
    
    # Pagination
    paginator = Paginator(posts, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Get categories for filter
    categories = Category.objects.filter(is_active=True)
    
    context = {
        'posts': page_obj,
        'page_obj': page_obj,
        'query': query,
        'categories': categories,
        'selected_category': category,
    }
    
    return render(request, 'blog/search.html', context)