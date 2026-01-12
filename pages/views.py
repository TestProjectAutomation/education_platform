from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.utils.translation import gettext_lazy as _
from .models import Page

def page_detail(request, slug):
    """عرض صفحة فردية"""
    page = get_object_or_404(Page, slug=slug, status='published')
    
    # التحقق من الصفحات الخاصة
    if page.status == 'private' and not request.user.is_authenticated:
        raise Http404(_("Page not found"))
    
    # زيادة المشاهدات (إذا كان مطلوبًا)
    if hasattr(page, 'views'):
        page.views += 1
        page.save(update_fields=['views'])
    
    # الحصول على القائمة الجانبية (إذا كانت الصفحة تدعمها)
    sidebar_pages = None
    if page.template in ['sidebar_left', 'sidebar_right']:
        sidebar_pages = Page.objects.filter(
            status='published',
            show_in_menu=True
        ).exclude(id=page.id)[:5]
    
    context = {
        'page': page,
        'sidebar_pages': sidebar_pages,
        'breadcrumbs': page.get_breadcrumbs(),
    }
    
    # استخدام القالب المناسب
    template_name = f'pages/{page.template}.html'
    
    return render(request, template_name, context)

def page_list(request):
    """عرض جميع الصفحات (للقائمة)"""
    pages = Page.objects.filter(
        status='published',
        show_in_menu=True,
        parent__isnull=True
    ).order_by('order')
    
    context = {
        'pages': pages,
    }
    
    return render(request, 'pages/list.html', context)