from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.views.i18n import set_language
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from rest_framework import permissions


urlpatterns = [
    path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('set-language/', set_language, name='set_language'),
]

# Internationalized URLs
urlpatterns += i18n_patterns(
    # Core
    path('', include('core.urls')),
    
    # Accounts
    path('accounts/', include('accounts.urls')),
    path('accounts/', include('allauth.urls')),
    
    # Content
    path('courses/', include('courses.urls')),
    path('articles/', include('articles.urls')),
    path('scholarships/', include('scholarships.urls')),
    path('books/', include('books.urls')),
    path('pages/', include('pages.urls')),
    
    # Dashboard
    path('dashboard/', include('dashboard.urls')),
    
    # Advertisements
    path('ads/', include('advertisements.urls')),
    
    # Error pages
    path('404/', TemplateView.as_view(template_name='404.html'), name='404'),
    path('500/', TemplateView.as_view(template_name='500.html'), name='500'),
    path('maintenance/', TemplateView.as_view(template_name='maintenance.html'), name='maintenance'),
    
    prefix_default_language=True,
)

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    

