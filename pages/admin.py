from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from ckeditor.widgets import CKEditorWidget
from .models import Page, PageComment, PageRating, PageView
from .forms import PageForm
import csv
from django.http import HttpResponse

class PageCommentInline(admin.TabularInline):
    model = PageComment
    extra = 0
    fields = ['user', 'content', 'is_approved', 'created_at']
    readonly_fields = ['created_at']
    can_delete = True
    show_change_link = True

class PageRatingInline(admin.TabularInline):
    model = PageRating
    extra = 0
    readonly_fields = ['created_at']
    can_delete = True

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    form = PageForm
    list_display = (
        'title_display', 'status_badge', 'template', 
        'order', 'show_in_menu_display', 'views', 
        'created_at_formatted', 'actions'
    )
    list_filter = (
        'status', 'template', 'show_in_menu', 
        'show_in_sitemap', 'created_at', 'author'
    )
    search_fields = ('title', 'content', 'slug', 'seo_title', 'seo_description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = (
        'created_at', 'updated_at', 'views', 
        'author_display', 'breadcrumbs_display'
    )
    filter_horizontal = ()
    list_per_page = 25
    date_hierarchy = 'created_at'
    save_on_top = True
    inlines = [PageCommentInline, PageRatingInline]
    
    fieldsets = (
        (_('Content'), {
            'fields': (
                'title', 'slug', 'content', 'excerpt',
                'featured_image', 'thumbnail'
            ),
            'classes': ('wide',),
        }),
        (_('Settings'), {
            'fields': (
                'template', 'status', 'order',
                'show_in_menu', 'show_in_sitemap', 'parent',
                'author', 'allow_comments'
            ),
            'classes': ('collapse', 'wide'),
        }),
        (_('SEO'), {
            'fields': (
                'seo_title', 'seo_description',
                'seo_keywords', 'canonical_url'
            ),
            'classes': ('collapse',),
        }),
        (_('Publishing'), {
            'fields': ('publish_date', 'expire_date'),
            'classes': ('collapse',),
        }),
        (_('Metadata'), {
            'fields': (
                'created_at', 'updated_at', 'views',
                'author_display', 'breadcrumbs_display'
            ),
            'classes': ('collapse',),
        }),
    )
    
    formfield_overrides = {
        'content': {'widget': CKEditorWidget},
    }
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.user = request.user
        return form
    
    def save_model(self, request, obj, form, change):
        if not obj.author and request.user:
            obj.author = request.user
        super().save_model(request, obj, form, change)
    
    def title_display(self, obj):
        return format_html(
            '<strong>{}</strong><br><small>{}</small>',
            obj.title,
            obj.slug
        )
    title_display.short_description = _('Title / Slug')
    title_display.admin_order_field = 'title'
    
    def status_badge(self, obj):
        colors = {
            'draft': 'gray',
            'published': 'green',
            'private': 'orange',
            'archived': 'red',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    status_badge.short_description = _('Status')
    status_badge.admin_order_field = 'status'
    
    def show_in_menu_display(self, obj):
        return format_html(
            '✓' if obj.show_in_menu else '✗'
        )
    show_in_menu_display.short_description = _('Menu')
    
    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%Y-%m-%d %H:%M')
    created_at_formatted.short_description = _('Created')
    created_at_formatted.admin_order_field = 'created_at'
    
    def author_display(self, obj):
        if obj.author:
            return format_html(
                '<a href="{}">{}</a>',
                reverse('admin:auth_user_change', args=[obj.author.id]),
                obj.author.get_full_name() or obj.author.username
            )
        return '-'
    author_display.short_description = _('Author')
    
    def breadcrumbs_display(self, obj):
        breadcrumbs = obj.get_breadcrumbs()
        html = []
        for i, crumb in enumerate(breadcrumbs):
            if i > 0:
                html.append(' → ')
            html.append(f'<a href="{crumb["url"]}">{crumb["title"]}</a>')
        return format_html(''.join(html))
    breadcrumbs_display.short_description = _('Breadcrumbs')
    
    def actions(self, obj):
        return format_html(
            '<a href="{}" target="_blank" style="margin-right: 10px;">👁️ View</a>'
            '<a href="{}" style="margin-right: 10px;">✏️ Edit</a>',
            obj.get_absolute_url(),
            reverse('admin:pages_page_change', args=[obj.id])
        )
    actions.short_description = _('Actions')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if not request.user.is_superuser:
            qs = qs.filter(author=request.user)
        return qs
    
    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        if not request.user.is_superuser:
            # Remove author from list display for non-superusers
            list_display = tuple(x for x in list_display if x != 'author')
        return list_display
    
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = ['title', 'slug', 'status', 'views', 'created_at']
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename={meta.verbose_name_plural}.csv'
        
        writer = csv.writer(response)
        writer.writerow(field_names)
        
        for obj in queryset:
            writer.writerow([getattr(obj, field) for field in field_names])
        
        return response
    
    export_as_csv.short_description = _('Export Selected as CSV')
    
    actions = ['export_as_csv']
    
    class Media:
        css = {
            'all': ('css/admin-custom.css',)
        }
        js = ('js/admin-custom.js',)


@admin.register(PageComment)
class PageCommentAdmin(admin.ModelAdmin):
    list_display = ('page', 'user', 'content_preview', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at', 'page')
    search_fields = ('content', 'user__username', 'page__title')
    list_editable = ('is_approved',)
    actions = ['approve_comments', 'disapprove_comments']
    
    def content_preview(self, obj):
        return obj.content[:100] + '...' if len(obj.content) > 100 else obj.content
    content_preview.short_description = _('Content')
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, _('Selected comments have been approved.'))
    approve_comments.short_description = _('Approve selected comments')
    
    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, _('Selected comments have been disapproved.'))
    disapprove_comments.short_description = _('Disapprove selected comments')


@admin.register(PageRating)
class PageRatingAdmin(admin.ModelAdmin):
    list_display = ('page', 'user', 'rating_stars', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('page__title', 'user__username')
    
    def rating_stars(self, obj):
        return '★' * obj.rating + '☆' * (5 - obj.rating)
    rating_stars.short_description = _('Rating')


@admin.register(PageView)
class PageViewAdmin(admin.ModelAdmin):
    list_display = ('page', 'ip_address', 'created_at')
    list_filter = ('created_at', 'page')
    search_fields = ('ip_address', 'page__title')
    readonly_fields = ('page', 'ip_address', 'user_agent', 'referrer', 'created_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False