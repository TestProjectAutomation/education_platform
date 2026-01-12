from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Article, Tag, Comment, Category, ArticleView, ArticleRating, Bookmark

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent', 'order', 'is_active', 'articles_count', 'created_at')
    list_filter = ('is_active', 'parent', 'created_at')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('order', 'is_active')
    readonly_fields = ('created_at', 'updated_at', 'articles_count_display')
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'description', 'parent')
        }),
        (_('Display Settings'), {
            'fields': ('order', 'is_active')
        }),
        (_('Statistics'), {
            'fields': ('articles_count_display',),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def articles_count(self, obj):
        return obj.articles.filter(status='published').count()
    articles_count.short_description = _('Articles')
    
    def articles_count_display(self, obj):
        return self.articles_count(obj)
    articles_count_display.short_description = _('Published Articles')

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'is_featured', 'views', 'articles_count', 'created_at')
    list_filter = ('is_featured', 'created_at')
    search_fields = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ('is_featured',)
    readonly_fields = ('views', 'created_at', 'updated_at')
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('name', 'slug', 'description')
        }),
        (_('Settings'), {
            'fields': ('is_featured',)
        }),
        (_('Statistics'), {
            'fields': ('views', 'articles_count_display')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at')
        }),
    )
    
    def articles_count(self, obj):
        return obj.article_set.filter(status='published').count()
    articles_count.short_description = _('Articles')
    
    def articles_count_display(self, obj):
        return self.articles_count(obj)
    articles_count_display.short_description = _('Published Articles')

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'views', 
                   'reading_time', 'is_featured', 'is_pinned', 'published_at')
    list_filter = ('status', 'category', 'is_featured', 'is_pinned', 
                  'is_premium', 'published_at', 'created_at')
    search_fields = ('title', 'content', 'excerpt', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views', 'created_at', 'updated_at', 'published_at', 
                      'rating_display', 'comments_count_display')
    filter_horizontal = ('tags', 'related_articles')
    date_hierarchy = 'published_at'
    actions = ['make_published', 'make_draft', 'feature_articles', 'pin_articles']
    
    fieldsets = (
        (_('Content'), {
            'fields': ('title', 'slug', 'content', 'excerpt', 'featured_image')
        }),
        (_('Details'), {
            'fields': ('reading_time', 'category', 'tags', 'related_articles')
        }),
        (_('Publishing'), {
            'fields': ('author', 'status', 'published_at', 'scheduled_for', 
                      'is_featured', 'is_pinned', 'is_premium', 'allow_comments')
        }),
        (_('SEO'), {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        (_('Statistics'), {
            'fields': ('views', 'rating_display', 'comments_count_display'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def rating_display(self, obj):
        avg = obj.ratings.aggregate(Avg('rating'))['rating__avg']
        if avg:
            return f'{avg:.1f} ⭐ ({obj.ratings.count()})'
        return _('No ratings')
    rating_display.short_description = _('Rating')
    
    def comments_count_display(self, obj):
        return obj.comments.filter(is_approved=True).count()
    comments_count_display.short_description = _('Comments')
    
    def make_published(self, request, queryset):
        updated = queryset.update(status='published', published_at=timezone.now())
        self.message_user(request, _('{count} articles published successfully.').format(count=updated))
    make_published.short_description = _("Publish selected articles")
    
    def make_draft(self, request, queryset):
        updated = queryset.update(status='draft')
        self.message_user(request, _('{count} articles marked as draft.').format(count=updated))
    make_draft.short_description = _("Mark selected articles as draft")
    
    def feature_articles(self, request, queryset):
        for article in queryset:
            article.is_featured = not article.is_featured
            article.save()
        self.message_user(request, _('Featured status toggled for selected articles.'))
    feature_articles.short_description = _("Toggle featured status")
    
    def pin_articles(self, request, queryset):
        for article in queryset:
            article.is_pinned = not article.is_pinned
            article.save()
        self.message_user(request, _('Pinned status toggled for selected articles.'))
    pin_articles.short_description = _("Toggle pinned status")
    
    def save_model(self, request, obj, form, change):
        if not change:
            obj.author = request.user
        super().save_model(request, obj, form, change)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'article_link', 'is_approved', 
                   'is_spam', 'created_at', 'content_preview')
    list_filter = ('is_approved', 'is_spam', 'created_at', 'article')
    search_fields = ('name', 'email', 'content', 'article__title')
    readonly_fields = ('created_at', 'updated_at', 'ip_address', 
                      'user_agent', 'likes', 'dislikes')
    actions = ['approve_comments', 'disapprove_comments', 'mark_as_spam', 'mark_as_not_spam']
    
    fieldsets = (
        (_('Content'), {
            'fields': ('article', 'parent', 'content')
        }),
        (_('Author'), {
            'fields': ('user', 'name', 'email', 'website')
        }),
        (_('Status'), {
            'fields': ('is_approved', 'is_spam', 'is_edited')
        }),
        (_('Statistics'), {
            'fields': ('likes', 'dislikes'),
            'classes': ('collapse',)
        }),
        (_('Tracking'), {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def article_link(self, obj):
        url = reverse('admin:articles_article_change', args=[obj.article.id])
        return format_html('<a href="{}">{}</a>', url, obj.article.title)
    article_link.short_description = _('Article')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = _('Content')
    
    def approve_comments(self, request, queryset):
        queryset.update(is_approved=True)
        self.message_user(request, _('Selected comments approved.'))
    approve_comments.short_description = _("Approve selected comments")
    
    def disapprove_comments(self, request, queryset):
        queryset.update(is_approved=False)
        self.message_user(request, _('Selected comments disapproved.'))
    disapprove_comments.short_description = _("Disapprove selected comments")
    
    def mark_as_spam(self, request, queryset):
        queryset.update(is_spam=True, is_approved=False)
        self.message_user(request, _('Selected comments marked as spam.'))
    mark_as_spam.short_description = _("Mark as spam")
    
    def mark_as_not_spam(self, request, queryset):
        queryset.update(is_spam=False)
        self.message_user(request, _('Selected comments marked as not spam.'))
    mark_as_not_spam.short_description = _("Mark as not spam")

@admin.register(ArticleView)
class ArticleViewAdmin(admin.ModelAdmin):
    list_display = ('article', 'ip_address', 'created_at')
    list_filter = ('created_at', 'article')
    search_fields = ('article__title', 'ip_address', 'user_agent')
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False

@admin.register(ArticleRating)
class ArticleRatingAdmin(admin.ModelAdmin):
    list_display = ('article', 'user', 'rating', 'ip_address', 'created_at')
    list_filter = ('rating', 'created_at', 'article')
    search_fields = ('article__title', 'user__username', 'ip_address')
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        return False

@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ('user', 'article', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'article__title')
    readonly_fields = ('created_at',)
    
    def has_add_permission(self, request):
        return False
