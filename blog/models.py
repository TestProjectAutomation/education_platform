from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.urls import reverse
from django.conf import settings
from ckeditor.fields import RichTextField
from PIL import Image
import os

class Category(models.Model):
    name_ar = models.CharField(_('الاسم بالعربية'), max_length=100)
    name_en = models.CharField(_('الاسم بالإنجليزية'), max_length=100)
    slug = models.SlugField(_('الرابط'), unique=True, max_length=100)
    description = models.TextField(_('الوصف'), blank=True)
    order = models.IntegerField(_('الترتيب'), default=0)
    is_active = models.BooleanField(_('نشط'), default=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)

    class Meta:
        verbose_name = _('التصنيف')
        verbose_name_plural = _('التصنيفات')
        ordering = ['order', 'name_ar']

    def __str__(self):
        return self.name_ar

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name_en)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('blog:category_detail', kwargs={'slug': self.slug})

    def get_name(self):
        return getattr(self, f'name_{self.get_current_language()}')

class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = 'draft', _('مسودة')
        PUBLISHED = 'published', _('منشور')
        PRIVATE = 'private', _('خاص')
        ARCHIVED = 'archived', _('مؤرشف')

    title = models.CharField(_('العنوان'), max_length=200)
    slug = models.SlugField(_('الرابط'), unique=True, max_length=200)
    content = RichTextField(_('المحتوى'))
    excerpt = models.TextField(_('المقتطف'), max_length=300, blank=True)
    
    featured_image = models.ImageField(_('الصورة الرئيسية'), upload_to='blog/featured/%Y/%m/')
    thumbnail = models.ImageField(_('الصورة المصغرة'), upload_to='blog/thumbnails/%Y/%m/', blank=True)
    
    category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name=_('التصنيف'))
    status = models.CharField(_('الحالة'), max_length=20, choices=Status.choices, default=Status.DRAFT)
    views = models.PositiveIntegerField(_('المشاهدات'), default=0)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name=_('المؤلف'))
    
    is_featured = models.BooleanField(_('مميز'), default=False)
    publish_date = models.DateTimeField(_('تاريخ النشر'), blank=True, null=True)
    created_at = models.DateTimeField(_('تاريخ الإنشاء'), auto_now_add=True)
    updated_at = models.DateTimeField(_('تاريخ التحديث'), auto_now=True)
    
    # SEO Fields
    seo_title = models.CharField(_('عنوان SEO'), max_length=200, blank=True)
    seo_description = models.TextField(_('وصف SEO'), max_length=300, blank=True)
    seo_keywords = models.CharField(_('كلمات مفتاحية SEO'), max_length=200, blank=True)
    canonical_url = models.URLField(_('رابط Canonical'), blank=True)

    class Meta:
        verbose_name = _('مقال')
        verbose_name_plural = _('المقالات')
        ordering = ['-publish_date', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-set publish_date if published and not set
        if self.status == self.Status.PUBLISHED and not self.publish_date:
            from django.utils import timezone
            self.publish_date = timezone.now()
        
        super().save(*args, **kwargs)
        
        # Create thumbnail if featured_image exists
        if self.featured_image and not self.thumbnail:
            self.create_thumbnail()

    def create_thumbnail(self):
        if not self.featured_image:
            return
        
        image = Image.open(self.featured_image.path)
        
        # Define thumbnail size
        thumb_size = (300, 200)
        image.thumbnail(thumb_size, Image.Resampling.LANCZOS)
        
        # Create thumbnail path
        thumb_path = self.featured_image.path.replace('featured', 'thumbnails')
        thumb_dir = os.path.dirname(thumb_path)
        
        # Create directory if not exists
        os.makedirs(thumb_dir, exist_ok=True)
        
        # Save thumbnail
        image.save(thumb_path)
        
        # Update thumbnail field
        thumb_url = self.featured_image.url.replace('featured', 'thumbnails')
        self.thumbnail.name = thumb_url.split('media/')[-1]
        self.save(update_fields=['thumbnail'])

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'slug': self.slug})

    def increase_views(self):
        self.views += 1
        self.save(update_fields=['views'])

    def get_related_posts(self, limit=3):
        return Post.objects.filter(
            category=self.category,
            status=Post.Status.PUBLISHED
        ).exclude(id=self.id)[:limit]

    @property
    def display_title(self):
        return self.seo_title or self.title

    @property
    def display_description(self):
        return self.seo_description or self.excerpt or self.content[:160]