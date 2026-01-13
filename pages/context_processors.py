from .models import Page

def pages_menu(request):
    """Add pages menu to all templates"""
    if request.user.is_authenticated:
        # Show all pages for authenticated users
        menu_pages = Page.objects.filter(
            status__in=['published', 'private'],
            show_in_menu=True,
            parent__isnull=True
        ).order_by('order')
    else:
        # Show only published pages for anonymous users
        menu_pages = Page.objects.filter(
            status='published',
            show_in_menu=True,
            parent__isnull=True
        ).order_by('order')
    
    return {
        'menu_pages': menu_pages
    }

def page_stats(request):
    """Add page statistics to context"""
    from django.db.models import Count
    
    stats = {
        'total_published_pages': Page.objects.filter(status='published').count(),
        'total_views': Page.objects.aggregate(Sum('views'))['views__sum'] or 0,
        'popular_pages': Page.objects.filter(status='published').order_by('-views')[:5],
    }
    
    return {
        'page_stats': stats
    }