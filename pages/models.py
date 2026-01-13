from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from ckeditor.fields import RichTextField
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings

class Page(models.Model):
    PAGE_STATUS = [
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('private', _('Private')),
        ('archived', _('Archived')),
    ]
    
    PAGE_TEMPLATES = [
        ('default', _('Default Template')),
        ('fullwidth', _('Full Width')),
        ('sidebar_left', _('Sidebar Left')),
        ('sidebar_right', _('Sidebar Right')),
        ('contact', _('Contact Page')),
        ('landing', _('Landing Page')),
    ]
    
    title = models.CharField(_('Title'), max_length=200)
    slug = models.SlugField(unique=True, max_length=250)
    content = RichTextField(_('Content'))
    excerpt = models.TextField(_('Excerpt'), blank=True, max_length=500)
    featured_image = models.ImageField(
        upload_to='pages/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text=_('Recommended size: 1200x630 pixels')
    )
    thumbnail = models.ImageField(
        upload_to='pages/thumbnails/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text=_('Recommended size: 300x200 pixels')
    )
    template = models.CharField(max_length=20, choices=PAGE_TEMPLATES, default='default')
    status = models.CharField(max_length=10, choices=PAGE_STATUS, default='draft')
    order = models.IntegerField(default=0, db_index=True)
    show_in_menu = models.BooleanField(default=True)
    show_in_sitemap = models.BooleanField(default=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    
    # SEO Fields
    seo_title = models.CharField(_('SEO Title'), max_length=200, blank=True)
    seo_description = models.TextField(_('SEO Description'), blank=True, max_length=300)
    seo_keywords = models.CharField(_('SEO Keywords'), max_length=200, blank=True)
    canonical_url = models.URLField(_('Canonical URL'), blank=True)
    
    # Metadata
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='pages')
    views = models.PositiveIntegerField(default=0, editable=False)
    allow_comments = models.BooleanField(default=False)
    
    # Dates
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    publish_date = models.DateTimeField(_('Publish Date'), null=True, blank=True)
    expire_date = models.DateTimeField(_('Expire Date'), null=True, blank=True)
    
    class Meta:
        ordering = ['order', 'title']
        verbose_name = _('Page')
        verbose_name_plural = _('Pages')
        indexes = [
            models.Index(fields=['status', 'publish_date']),
            models.Index(fields=['slug']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # Auto-generate SEO title if empty
        if not self.seo_title:
            self.seo_title = self.title
        
        # Auto-generate excerpt from content if empty
        if not self.excerpt and self.content:
            self.excerpt = self.content[:497] + '...' if len(self.content) > 500 else self.content
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        if not self.slug:
            return ""
        return reverse('pages:detail', kwargs={'slug': self.slug})
    
        
    def get_breadcrumbs(self):
        breadcrumbs = []
        page = self
        
        while page:
            breadcrumbs.insert(0, {
                'title': page.title,
                'url': page.get_absolute_url()
            })
            page = page.parent
        
        # Add home page
        breadcrumbs.insert(0, {
            'title': _('Home'),
            'url': '/'
        })
        
        return breadcrumbs
    
    def is_published(self):
        from django.utils import timezone
        now = timezone.now()
        
        if self.status != 'published':
            return False
        
        if self.publish_date and self.publish_date > now:
            return False
        
        if self.expire_date and self.expire_date < now:
            return False
        
        return True
    
    def get_related_pages(self, limit=5):
        """Get related pages based on category/tags or similar content"""
        # Implementation can be extended based on requirements
        return Page.objects.filter(
            status='published',
            parent=self.parent
        ).exclude(id=self.id)[:limit]
    
    def increment_views(self):
        self.views = models.F('views') + 1
        self.save(update_fields=['views'])


class PageComment(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='page_comments')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    content = models.TextField(_('Comment'))
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Page Comment')
        verbose_name_plural = _('Page Comments')
    
    def __str__(self):
        return f'Comment by {self.user} on {self.page}'


class PageRating(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='page_ratings')
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['page', 'user']
        verbose_name = _('Page Rating')
        verbose_name_plural = _('Page Ratings')
    
    def __str__(self):
        return f'{self.rating} stars by {self.user} on {self.page}'


class PageView(models.Model):
    page = models.ForeignKey(Page, on_delete=models.CASCADE, related_name='page_views')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Page View')
        verbose_name_plural = _('Page Views')
        indexes = [
            models.Index(fields=['page', 'created_at']),
        ]


class TimedContent(models.Model):
    title = models.CharField(_('Title'), max_length=200)
    content = RichTextField(_('Content'))
    link = models.URLField(_('Link'), blank=True)
    link_text = models.CharField(_('Link Text'), max_length=100, blank=True)
    link_display_delay = models.PositiveIntegerField(
        _('Link Display Delay (seconds)'),
        default=30,
        help_text=_('Time in seconds before the link becomes visible')
    )
    is_active = models.BooleanField(default=True)
    publish_date = models.DateTimeField()
    expire_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        abstract = True
        ordering = ['-publish_date']
    
    def is_visible(self):
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active and 
            self.publish_date <= now and 
            (self.expire_date is None or self.expire_date > now)
        )