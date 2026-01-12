from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import SiteSetting, Category

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'contact_email', 'default_language', 'maintenance_mode')
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('site_name', 'site_description', 'logo', 'favicon')
        }),
        (_('Contact Information'), {
            'fields': ('contact_email',)
        }),
        (_('Social Media'), {
            'fields': ('facebook_url', 'twitter_url', 'linkedin_url', 'instagram_url', 'youtube_url')
        }),
        (_('Settings'), {
            'fields': ('default_language', 'maintenance_mode')
        }),
    )
    
    def has_add_permission(self, request):
        # Allow only one site setting
        return not SiteSetting.objects.exists()

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order', 'icon')
    list_editable = ('order', 'icon')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}