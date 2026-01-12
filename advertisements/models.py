from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.cache import cache

class AdPlacement(models.Model):
    PLACEMENT_CHOICES = [
        ('header', _('Header')),
        ('sidebar', _('Sidebar')),
        ('footer', _('Footer')),
        ('between_posts', _('Between Posts')),
        ('popup', _('Popup')),
        ('in_content', _('In Content')),
    ]
    
    name = models.CharField(_('Placement Name'), max_length=100)
    code = models.SlugField(unique=True)
    placement_type = models.CharField(max_length=20, choices=PLACEMENT_CHOICES)
    description = models.TextField(blank=True)
    width = models.PositiveIntegerField(default=300)
    height = models.PositiveIntegerField(default=250)
    active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

class Advertisement(models.Model):
    AD_TYPE_CHOICES = [
        ('banner', _('Banner Image')),
        ('text', _('Text Ad')),
        ('html', _('HTML Code')),
        ('video', _('Video Ad')),
    ]
    
    title = models.CharField(_('Ad Title'), max_length=200)
    placement = models.ForeignKey(AdPlacement, on_delete=models.CASCADE)
    ad_type = models.CharField(max_length=10, choices=AD_TYPE_CHOICES, default='banner')
    image = models.ImageField(upload_to='ads/', blank=True, null=True)
    text_content = models.TextField(blank=True)
    html_code = models.TextField(blank=True)
    video_url = models.URLField(blank=True)
    link = models.URLField()
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-start_date']
    
    def __str__(self):
        return self.title
    
    def is_active(self):
        from django.utils import timezone
        return self.active and self.start_date <= timezone.now() <= self.end_date
    
    def record_impression(self):
        self.impressions += 1
        self.save(update_fields=['impressions'])
    
    def record_click(self):
        self.clicks += 1
        self.save(update_fields=['clicks'])