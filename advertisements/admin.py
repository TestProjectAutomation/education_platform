from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Advertisement, AdPlacement

@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'placement', 'ad_type', 'start_date', 'end_date', 'active', 'impressions', 'clicks')
    list_filter = ('active', 'ad_type', 'placement', 'start_date', 'end_date')
    search_fields = ('title', 'text_content', 'link')
    readonly_fields = ('impressions', 'clicks')
    date_hierarchy = 'start_date'
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'placement', 'ad_type', 'active')
        }),
        (_('Content'), {
            'fields': ('image', 'text_content', 'html_code', 'video_url', 'link')
        }),
        (_('Schedule'), {
            'fields': ('start_date', 'end_date')
        }),
        (_('Statistics'), {
            'fields': ('impressions', 'clicks')
        }),
    )
    
    def save_model(self, request, obj, form, change):
        # Clear cache when ad is updated
        from django.core.cache import cache
        super().save_model(request, obj, form, change)
        cache.delete_pattern('active_ads_*')

@admin.register(AdPlacement)
class AdPlacementAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'placement_type', 'width', 'height', 'active')
    list_filter = ('placement_type', 'active')
    search_fields = ('name', 'code', 'description')
    prepopulated_fields = {'code': ('name',)}
    
    def save_model(self, request, obj, form, change):
        # Clear cache when placement is updated
        from django.core.cache import cache
        super().save_model(request, obj, form, change)
        cache.delete_pattern('active_ads_*')