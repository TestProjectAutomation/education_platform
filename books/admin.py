from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Book, BookReview, DownloadHistory

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'book_type', 'publication_year', 'views', 'status')
    list_filter = ('book_type', 'status', 'is_featured', 'publication_year')
    search_fields = ('title', 'author', 'content', 'isbn')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views',)
    filter_horizontal = ('categories',)
    
    fieldsets = (
        (_('Basic Information'), {
            'fields': ('title', 'slug', 'content', 'excerpt', 'featured_image')
        }),
        (_('Book Details'), {
            'fields': ('book_type', 'author', 'publisher', 'publication_year', 'pages', 'isbn')
        }),
        (_('Files & Links'), {
            'fields': ('download_link', 'file', 'preview_pages')
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

@admin.register(BookReview)
class BookReviewAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'book', 'rating', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'rating', 'created_at')
    search_fields = ('name', 'email', 'comment', 'book__title')
    readonly_fields = ('created_at',)
    actions = ['approve_reviews']

@admin.register(DownloadHistory)
class DownloadHistoryAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'ip_address', 'downloaded_at')
    list_filter = ('downloaded_at',)
    search_fields = ('book__title', 'user__username', 'ip_address')
    readonly_fields = ('downloaded_at', 'user_agent')