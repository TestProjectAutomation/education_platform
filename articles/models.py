from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseContent, Category

class Article(BaseContent):
    reading_time = models.PositiveIntegerField(_('Reading Time (minutes)'), default=5)
    tags = models.ManyToManyField('Tag', blank=True)
    
    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')

class Tag(models.Model):
    name = models.CharField(_('Tag Name'), max_length=50)
    slug = models.SlugField(unique=True)
    
    def __str__(self):
        return self.name

class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(_('Name'), max_length=100)
    email = models.EmailField()
    content = models.TextField(_('Comment'))
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.name} on {self.article.title}"