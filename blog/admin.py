from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from .models import Category, Post

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name_ar', 'name_en', 'slug', 'order', 'is_active', 'post_count', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name_ar', 'name_en', 'slug')
    prepopulated_fields = {'slug': ('name_en',)}
    ordering = ('order', 'name_ar')
    
    def post_count(self, obj):
        return obj.post_set.count()
    post_count.short_description = _('عدد المقالات')

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'is_featured', 'views', 
                   'publish_date', 'created_at', 'view_on_site_link')
    list_filter = ('status', 'category', 'is_featured', 'publish_date')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views', 'created_at', 'updated_at')
    date_hierarchy = 'publish_date'
    ordering = ('-publish_date', '-created_at')
    
    fieldsets = (
        (_('المعلومات الأساسية'), {
            'fields': ('title', 'slug', 'content', 'excerpt', 'category', 'author')
        }),
        (_('الصور'), {
            'fields': ('featured_image', 'thumbnail')
        }),
        (_('الإعدادات'), {
            'fields': ('status', 'is_featured', 'publish_date')
        }),
        (_('إحصائيات'), {
            'fields': ('views', 'created_at', 'updated_at')
        }),
        (_('SEO'), {
            'fields': ('seo_title', 'seo_description', 'seo_keywords', 'canonical_url'),
            'classes': ('collapse',)
        }),
    )
    
    def view_on_site_link(self, obj):
        if obj.pk and obj.status == Post.Status.PUBLISHED:
            url = obj.get_absolute_url()
            return format_html('<a href="{}" target="_blank">عرض</a>', url)
        return '-'
    view_on_site_link.short_description = _('عرض في الموقع')
    
    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)
    
    actions = ['make_published', 'make_draft', 'make_featured']
    
    @admin.action(description=_('نشر المقالات المحددة'))
    def make_published(self, request, queryset):
        queryset.update(status=Post.Status.PUBLISHED)
    
    @admin.action(description=_('تحويل إلى مسودة'))
    def make_draft(self, request, queryset):
        queryset.update(status=Post.Status.DRAFT)
    
    @admin.action(description=_('تحديد كمميز'))
    def make_featured(self, request, queryset):
        queryset.update(is_featured=True)