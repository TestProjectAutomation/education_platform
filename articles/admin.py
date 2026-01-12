from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Article, Tag, Comment

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'status', 'reading_time', 'views', 'created_at')
    list_filter = ('status', 'created_at', 'is_featured')
    search_fields = ('title', 'content', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views',)
    filter_horizontal = ('categories', 'tags')
    
    fieldsets = (
        (_('Content'), {
            'fields': ('title', 'slug', 'content', 'excerpt', 'featured_image')
        }),
        (_('Details'), {
            'fields': ('reading_time', 'link_display_duration')
        }),
        (_('Categorization'), {
            'fields': ('categories', 'tags')
        }),
        (_('Publishing'), {
            'fields': ('author', 'status', 'is_featured')
        }),
        (_('Statistics'), {
            'fields': ('views',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'article', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'created_at')
    search_fields = ('name', 'email', 'content', 'article__title')
    readonly_fields = ('created_at',)
    actions = ['approve_comments', 'disapprove_comments']
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
    approve_comments.short_description = _("Approve selected comments")
    
    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
    disapprove_comments.short_description = _("Disapprove selected comments")