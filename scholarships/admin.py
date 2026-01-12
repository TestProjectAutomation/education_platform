from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Scholarship, ApplicationTip

class ApplicationTipInline(admin.TabularInline):
    model = ApplicationTip
    extra = 1
    fields = ('title', 'content', 'order')

@admin.register(Scholarship)
class ScholarshipAdmin(admin.ModelAdmin):
    list_display = ('title', 'country', 'university', 'deadline', 'is_featured', 'status')
    list_filter = ('status', 'scholarship_type', 'country', 'is_featured', 'deadline')
    search_fields = ('title', 'university', 'country', 'content')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views',)
    filter_horizontal = ('categories',)
    inlines = [ApplicationTipInline]
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'slug', 'content', 'excerpt', 'featured_image')
        }),
        (_('Scholarship Details'), {
            'fields': ('scholarship_type', 'country', 'university', 'deadline', 'funding_amount')
        }),
        (_('Requirements & Process'), {
            'fields': ('eligibility', 'application_process', 'official_link')
        }),
        (_('Categorization'), {
            'fields': ('categories',)
        }),
        (_('Publishing'), {
            'fields': ('link_display_duration', 'status', 'is_featured')
        }),
        (_('Statistics'), {
            'fields': ('views',)
        }),
    )

@admin.register(ApplicationTip)
class ApplicationTipAdmin(admin.ModelAdmin):
    list_display = ('title', 'scholarship', 'order')
    list_filter = ('scholarship',)
    search_fields = ('title', 'content')
    ordering = ('scholarship', 'order')