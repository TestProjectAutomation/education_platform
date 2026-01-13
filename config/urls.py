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
    path('i18n/', include('django.conf.urls.i18n')),
]

# Internationalized URLs
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    # Core
    path('', include('core.urls')),
    
    # Accounts
    path("accounts/", include("accounts.urls")),
    
    # Content
    path('articles/', include('articles.urls')),
    path('books/', include('books.urls')),
    path('pages/', include('pages.urls')),
    path('blog/', include('blog.urls')),
    # Dashboard
    # path('dashboard/', include('dashboard.urls')),
    
    # Advertisements
    path('ads/', include('advertisements.urls')),
    
    # Error pages
    path('404/', TemplateView.as_view(template_name='erorr/404.html'), name='404'),
    path('500/', TemplateView.as_view(template_name='erorr/500.html'), name='500'),
    path('maintenance/', TemplateView.as_view(template_name='erorr/maintenance.html'), name='maintenance'),
    
    prefix_default_language=True,
)

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    

