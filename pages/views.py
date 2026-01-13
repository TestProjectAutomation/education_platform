from django.shortcuts import render, get_object_or_404, redirect
from django.http import Http404, JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.db.models import Q, Count, Avg
from django.views.decorators.http import require_POST
from django.views.decorators.cache import cache_page
from django.views.generic import ListView, DetailView
from django.core.cache import cache
import json

from .models import Page, PageComment, PageRating, PageView
from .forms import PageCommentForm, PageRatingForm, PageSearchForm

def get_client_ip(request):
    """Get client IP address"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@cache_page(60 * 15)  # Cache for 15 minutes
def page_detail(request, slug):
    """Display single page with enhanced features"""
    # Try to get from cache first
    cache_key = f'page_detail_{slug}_{request.LANGUAGE_CODE}'
    cached_page = cache.get(cache_key)
    
    if cached_page and not request.user.is_staff:
        return cached_page
    
    page = get_object_or_404(Page, slug=slug)
    
    # Check page accessibility
    if not page.is_published():
        if not request.user.is_staff:
            raise Http404(_("Page not found"))
    
    if page.status == 'private' and not request.user.is_authenticated:
        raise Http404(_("Page not found"))
    
    # Track page view
    if not request.user.is_staff:  # Don't track admin views
        page.increment_views()
        
        # Save detailed view info
        PageView.objects.create(
            page=page,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            referrer=request.META.get('HTTP_REFERER', '')
        )
    
    # Get sidebar pages
    sidebar_pages = None
    if page.template in ['sidebar_left', 'sidebar_right']:
        sidebar_pages = Page.objects.filter(
            status='published',
            show_in_menu=True
        ).exclude(id=page.id).order_by('-views')[:5]
    
    # Get comments
    comments = page.comments.filter(is_approved=True).order_by('-created_at')
    
    # Get average rating
    avg_rating = page.ratings.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Check if user has rated
    user_rating = None
    if request.user.is_authenticated:
        user_rating = page.ratings.filter(user=request.user).first()
    
    # Get related pages
    related_pages = page.get_related_pages(limit=3)
    
    # Comment form
    comment_form = PageCommentForm()
    
    # Rating form
    rating_form = PageRatingForm()
    
    context = {
        'page': page,
        'sidebar_pages': sidebar_pages,
        'breadcrumbs': page.get_breadcrumbs(),
        'comments': comments,
        'comment_form': comment_form,
        'rating_form': rating_form,
        'avg_rating': round(avg_rating, 1),
        'user_rating': user_rating,
        'related_pages': related_pages,
        'meta_title': page.seo_title or page.title,
        'meta_description': page.seo_description or page.excerpt,
        'meta_keywords': page.seo_keywords,
        'canonical_url': page.canonical_url or request.build_absolute_uri(),
    }
    
    # Use appropriate template
    template_name = f'pages/{page.template}.html'
    
    response = render(request, template_name, context)
    
    # Cache the response
    if page.status == 'published':
        cache.set(cache_key, response, 60 * 15)
    
    return response

def page_list(request):
    """Display all pages with filtering and pagination"""
    form = PageSearchForm(request.GET or None)
    
    pages = Page.objects.filter(
        status='published',
        show_in_menu=True,
        parent__isnull=True
    ).order_by('order', '-created_at')
    
    if form.is_valid():
        q = form.cleaned_data.get('q')
        category = form.cleaned_data.get('category')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        
        if q:
            pages = pages.filter(
                Q(title__icontains=q) |
                Q(content__icontains=q) |
                Q(excerpt__icontains=q)
            )
        
        if category:
            pages = pages.filter(parent_id=category)
        
        if date_from:
            pages = pages.filter(created_at__date__gte=date_from)
        
        if date_to:
            pages = pages.filter(created_at__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(pages, 12)  # 12 pages per page
    page_number = request.GET.get('page')
    
    try:
        page_obj = paginator.page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)
    
    context = {
        'pages': page_obj,
        'form': form,
        'page_obj': page_obj,
    }
    
    return render(request, 'pages/list.html', context)

@require_POST
@login_required
def add_comment(request, slug):
    """Add comment to page"""
    page = get_object_or_404(Page, slug=slug)
    
    if not page.allow_comments:
        return JsonResponse({'error': _('Comments are not allowed for this page')}, status=403)
    
    form = PageCommentForm(request.POST)
    
    if form.is_valid():
        comment = form.save(commit=False)
        comment.page = page
        comment.user = request.user
        
        # Auto-approve comments for staff users
        if request.user.is_staff:
            comment.is_approved = True
        
        comment.save()
        
        # Send notification email (optional)
        # send_comment_notification(comment)
        
        messages.success(request, _('Your comment has been submitted successfully.'))
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': _('Comment added successfully'),
                'comment_id': comment.id
            })
        
        return redirect(page.get_absolute_url())
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'errors': form.errors}, status=400)
    
    messages.error(request, _('There was an error with your comment.'))
    return redirect(page.get_absolute_url())

@require_POST
@login_required
def add_rating(request, slug):
    """Add or update page rating"""
    page = get_object_or_404(Page, slug=slug)
    
    form = PageRatingForm(request.POST)
    
    if form.is_valid():
        rating, created = PageRating.objects.update_or_create(
            page=page,
            user=request.user,
            defaults={'rating': form.cleaned_data['rating']}
        )
        
        # Calculate new average
        avg_rating = page.ratings.aggregate(Avg('rating'))['rating__avg'] or 0
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': _('Rating submitted successfully'),
                'avg_rating': round(avg_rating, 1),
                'total_ratings': page.ratings.count(),
                'user_rating': rating.rating
            })
        
        messages.success(request, _('Thank you for your rating!'))
        return redirect(page.get_absolute_url())
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'errors': form.errors}, status=400)
    
    messages.error(request, _('There was an error with your rating.'))
    return redirect(page.get_absolute_url())

def page_sitemap(request):
    """Generate sitemap for pages"""
    pages = Page.objects.filter(
        status='published',
        show_in_sitemap=True,
        parent__isnull=True
    ).order_by('-updated_at')
    
    context = {
        'pages': pages,
        'lastmod': pages.first().updated_at if pages.exists() else None,
    }
    
    return render(request, 'pages/sitemap.xml', context, content_type='application/xml')

def page_search(request):
    """Advanced search for pages"""
    query = request.GET.get('q', '')
    results = []
    
    if query:
        results = Page.objects.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query) |
            Q(excerpt__icontains=query) |
            Q(seo_description__icontains=query),
            status='published'
        ).order_by('-created_at')
    
    context = {
        'query': query,
        'results': results,
        'results_count': results.count(),
    }
    
    return render(request, 'pages/search.html', context)

@login_required
@permission_required('pages.add_page', raise_exception=True)
def page_preview(request, slug):
    """Preview page for editors"""
    page = get_object_or_404(Page, slug=slug)
    
    # Only allow preview for draft/private pages
    if page.status not in ['draft', 'private'] and not request.user.is_superuser:
        return HttpResponseForbidden(_('You cannot preview this page'))
    
    context = {
        'page': page,
        'preview_mode': True,
        'breadcrumbs': page.get_breadcrumbs(),
    }
    
    return render(request, f'pages/{page.template}.html', context)

class PageListView(ListView):
    """Class-based view for page list"""
    model = Page
    template_name = 'pages/list_class.html'
    context_object_name = 'pages'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.filter(
            status='published',
            show_in_menu=True,
            parent__isnull=True
        )
        
        # Apply search
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            )
        
        return queryset.order_by('order', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = PageSearchForm(self.request.GET or None)
        return context

class PageDetailView(DetailView):
    """Class-based view for page detail"""
    model = Page
    template_name = 'pages/detail_class.html'
    context_object_name = 'page'
    
    def get_template_names(self):
        page = self.get_object()
        return [f'pages/{page.template}.html']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # For non-staff users, only show published pages
        if not self.request.user.is_staff:
            queryset = queryset.filter(status='published')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        page = self.get_object()
        
        # Track view
        if not self.request.user.is_staff:
            page.increment_views()
        
        # Add additional context
        context.update({
            'sidebar_pages': Page.objects.filter(
                status='published',
                show_in_menu=True
            ).exclude(id=page.id).order_by('-views')[:5],
            'breadcrumbs': page.get_breadcrumbs(),
            'comments': page.comments.filter(is_approved=True).order_by('-created_at'),
            'comment_form': PageCommentForm(),
            'rating_form': PageRatingForm(),
            'avg_rating': page.ratings.aggregate(Avg('rating'))['rating__avg'] or 0,
            'related_pages': page.get_related_pages(limit=3),
        })
        
        return context