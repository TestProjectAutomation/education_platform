from django.db import models
from django.utils.translation import gettext_lazy as _
from ckeditor.fields import RichTextField

class Page(models.Model):
    PAGE_STATUS = [
        ('draft', _('Draft')),
        ('published', _('Published')),
        ('private', _('Private')),
    ]
    
    PAGE_TEMPLATES = [
        ('default', _('Default Template')),
        ('fullwidth', _('Full Width')),
        ('sidebar_left', _('Sidebar Left')),
        ('sidebar_right', _('Sidebar Right')),
    ]
    
    title = models.CharField(_('Title'), max_length=200)
    slug = models.SlugField(unique=True)
    content = RichTextField(_('Content'))
    excerpt = models.TextField(_('Excerpt'), blank=True)
    featured_image = models.ImageField(upload_to='pages/', blank=True, null=True)
    template = models.CharField(max_length=20, choices=PAGE_TEMPLATES, default='default')
    status = models.CharField(max_length=10, choices=PAGE_STATUS, default='draft')
    order = models.IntegerField(default=0)
    show_in_menu = models.BooleanField(default=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    seo_title = models.CharField(_('SEO Title'), max_length=200, blank=True)
    seo_description = models.TextField(_('SEO Description'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'title']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
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
        
        return breadcrumbs
    


class TimedContent(models.Model):
    title = models.CharField(_('Title'), max_length=200)
    content = models.TextField(_('Content'))
    link = models.URLField(_('Link'), blank=True)
    link_text = models.CharField(_('Link Text'), max_length=100, blank=True)
    link_display_delay = models.PositiveIntegerField(
        _('Link Display Delay (seconds)'),
        default=30,
        help_text=_('Time in seconds before the link becomes visible')
    )
    is_active = models.BooleanField(default=True)
    publish_date = models.DateTimeField()
    
    class Meta:
        abstract = True
    
    def is_visible(self):
        from django.utils import timezone
        return self.is_active and self.publish_date <= timezone.now()