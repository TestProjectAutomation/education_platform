from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseContent

class Book(BaseContent):
    TYPE_CHOICES = [
        ('book', _('Book')),
        ('summary', _('Summary')),
        ('notes', _('Study Notes')),
    ]
    
    book_type = models.CharField(_('Type'), max_length=20, choices=TYPE_CHOICES, default='book')
    author = models.CharField(_('Author'), max_length=200)
    publisher = models.CharField(_('Publisher'), max_length=200, blank=True)
    publication_year = models.PositiveIntegerField(_('Publication Year'), null=True, blank=True)
    pages = models.PositiveIntegerField(_('Number of Pages'), null=True, blank=True)
    isbn = models.CharField(_('ISBN'), max_length=20, blank=True)
    download_link = models.URLField(_('Download Link'), blank=True)
    file = models.FileField(_('File'), upload_to='books/', blank=True, null=True)
    preview_pages = models.PositiveIntegerField(_('Preview Pages'), default=10)
    
    class Meta:
        verbose_name = _('Book')
        verbose_name_plural = _('Books')
    
    @property
    def file_type(self):
        if self.file:
            return self.file.name.split('.')[-1].upper()
        return None

class BookReview(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    name = models.CharField(_('Name'), max_length=100)
    email = models.EmailField()
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField(_('Comment'))
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Review by {self.name} for {self.book.title}"

class DownloadHistory(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField()
    downloaded_at = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = _('Download History')