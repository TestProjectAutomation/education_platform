from django.utils import translation
from django.utils.deprecation import MiddlewareMixin
from django.http import HttpResponseRedirect
from .models import SiteSetting

class SiteMaintenanceMiddleware(MiddlewareMixin):
    """ميدلوير وضع الصيانة"""
    def process_request(self, request):
        # تجاوز وضع الصيانة للمسؤولين
        if request.user.is_superuser or request.path.startswith('/admin/'):
            return None
        
        try:
            settings = SiteSetting.objects.first()
            if settings and settings.maintenance_mode:
                # السماح ببعض الصفحات أثناء الصيانة
                allowed_paths = ['/accounts/login/', '/accounts/logout/', '/maintenance/']
                if not any(request.path.startswith(path) for path in allowed_paths):
                    return HttpResponseRedirect('/maintenance/')
        except:
            pass
        
        return None

class LanguageMiddleware(MiddlewareMixin):
    """ميدلوير اللغة"""
    def process_request(self, request):
        language = translation.get_language_from_request(request)
        
        # التحقق من وجود إعدادات الموقع
        try:
            settings = SiteSetting.objects.first()
            if settings:
                # استخدام اللغة الافتراضية من الإعدادات
                if not language or language not in ['ar', 'en']:
                    language = settings.default_language
        except:
            # اللغة الافتراضية العربية
            language = language or 'ar'
        
        translation.activate(language)
        request.LANGUAGE_CODE = language
        
        return None