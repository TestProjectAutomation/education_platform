from django.core.cache import cache
from django.utils.translation import gettext_lazy as _
from .models import SiteSetting, Category
from advertisements.models import Advertisement, AdPlacement
from pages.models import Page

def site_settings(request):
    """إرجاع إعدادات الموقع المخزنة في الكاش"""
    settings = cache.get('site_settings')
    
    if not settings:
        settings = SiteSetting.objects.first()
        if not settings:
            # إعدادات افتراضية إذا لم يتم إعدادها
            settings = SiteSetting(
                site_name="منصة التعليم",
                site_description="منصة تعليمية متكاملة",
                default_language="ar"
            )
        # تخزين في الكاش لمدة ساعة
        cache.set('site_settings', settings, 3600)
    
    return {'site_settings': settings}

def language_processor(request):
    """معالج إعدادات اللغة"""
    return {
        'current_language': request.LANGUAGE_CODE,
        'is_rtl': request.LANGUAGE_CODE == 'ar',
    }

def dark_mode_processor(request):
    """معالج الوضع المظلم"""
    dark_mode = False
    
    if request.user.is_authenticated:
        dark_mode = request.user.dark_mode
    elif 'dark_mode' in request.COOKIES:
        dark_mode = request.COOKIES.get('dark_mode') == 'true'
    
    return {'dark_mode': dark_mode}

def menu_categories(request):
    """إرجاع التصنيفات للقائمة"""
    categories = cache.get('menu_categories')
    
    if not categories:
        categories = Category.objects.filter(order__gte=0).order_by('order')
        cache.set('menu_categories', categories, 300)
    
    return {'menu_categories': categories}

def main_menu_pages(request):
    """الصفحات الرئيسية للقائمة"""
    pages = cache.get('main_menu_pages')
    
    if not pages:
        pages = Page.objects.filter(
            status='published',
            show_in_menu=True,
            parent__isnull=True
        ).order_by('order')
        cache.set('main_menu_pages', pages, 300)
    
    return {'main_menu_pages': pages}

def active_advertisements(request):
    """الإعلانات النشطة للمواقع المختلفة"""
    if request.path.startswith('/admin/'):
        return {'active_ads': {}}
    
    ads_cache_key = f'active_ads_{request.LANGUAGE_CODE}'
    ads = cache.get(ads_cache_key)
    
    if not ads:
        placements = AdPlacement.objects.filter(active=True)
        ads_dict = {}
        
        for placement in placements:
            active_ad = Advertisement.objects.filter(
                placement=placement,
                active=True
            ).first()
            
            if active_ad and active_ad.is_active():
                ads_dict[placement.code] = active_ad
        
        cache.set(ads_cache_key, ads_dict, 60)  # تخزين لمدة دقيقة
    
    return {'active_ads': ads or {}}