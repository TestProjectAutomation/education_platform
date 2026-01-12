from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from ckeditor.widgets import CKEditorWidget
from .models import Page

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'template', 'status', 'order', 'show_in_menu', 'created_at')
    list_filter = ('status', 'template', 'show_in_menu', 'created_at')
    search_fields = ('title', 'content', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ()
    
    fieldsets = (
        (_('Content'), {
            'fields': ('title', 'slug', 'content', 'excerpt', 'featured_image')
        }),
        (_('Settings'), {
            'fields': ('template', 'status', 'order', 'show_in_menu', 'parent')
        }),
        (_('SEO'), {
            'fields': ('seo_title', 'seo_description')
        }),
        (_('Dates'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    formfield_overrides = {
        'content': {'widget': CKEditorWidget},
    }
    
    class Media:
        css = {
            'all': ('css/admin-custom.css',)
        }