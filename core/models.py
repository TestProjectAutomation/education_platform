from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache

class SiteSetting(models.Model):
    site_name = models.CharField(_('Site Name'), max_length=100)
    site_description = models.TextField(_('Site Description'))
    logo = models.ImageField(upload_to='site/')
    favicon = models.ImageField(upload_to='site/')
    contact_email = models.EmailField()
    facebook_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    default_language = models.CharField(max_length=2, default='ar')
    maintenance_mode = models.BooleanField(default=False)
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)
        # Clear cache when settings are updated
        cache.delete('site_settings')

class Category(models.Model):
    name = models.CharField(_('Category Name'), max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        verbose_name_plural = _('Categories')
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class BaseContent(models.Model):
    title = models.CharField(_('Title'), max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField(_('Content'))
    excerpt = models.TextField(_('Excerpt'), blank=True)
    featured_image = models.ImageField(upload_to='content/')
    categories = models.ManyToManyField(Category, blank=True)
    author = models.ForeignKey('accounts.CustomUser', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=[
        ('draft', _('Draft')),
        ('published', _('Published'))
    ], default='draft')
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    link_display_duration = models.PositiveIntegerField(_('Link Display Duration (seconds)'), default=30)
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def increment_views(self):
        self.views += 1
        self.save(update_fields=['views'])