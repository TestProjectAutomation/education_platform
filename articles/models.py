from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from core.models import BaseContent
from django.conf import settings

class Category(models.Model):
    """تصنيفات المقالات"""
    name = models.CharField(_('Category Name'), max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(_('Description'), blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                              related_name='children', verbose_name=_('Parent Category'))
    order = models.IntegerField(_('Display Order'), default=0)
    is_active = models.BooleanField(_('Is Active'), default=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('articles:category', kwargs={'slug': self.slug})
    
    def get_articles_count(self):
        """عدد المقالات في هذا التصنيف"""
        return self.articles.filter(status='published').count()
    
    @property
    def children_count(self):
        """عدد الأقسام الفرعية"""
        return self.children.filter(is_active=True).count()

class Tag(models.Model):
    """وسوم المقالات"""
    name = models.CharField(_('Tag Name'), max_length=50)
    slug = models.SlugField(unique=True)
    description = models.TextField(_('Description'), blank=True)
    views = models.PositiveIntegerField(_('Views'), default=0)
    is_featured = models.BooleanField(_('Is Featured'), default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
        
    class Meta:
        verbose_name = _('Tag')
        verbose_name_plural = _('Tags')
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('articles:tag', kwargs={'slug': self.slug})
    
    def get_articles_count(self):
        """عدد المقالات في هذا الوسم"""
        return self.article_set.filter(status='published').count()

class Article(BaseContent):
    """نموذج المقالات"""
    STATUS_CHOICES = (
        ('draft', _('Draft')),
        ('review', _('Under Review')),
        ('published', _('Published')),
        ('archived', _('Archived')),
    )
    
    # معلومات إضافية
    reading_time = models.PositiveIntegerField(_('Reading Time (minutes)'), default=5)
    views = models.PositiveIntegerField(_('Views'), default=0)
    featured_image = models.ImageField(_('Featured Image'), upload_to='articles/featured/%Y/%m/', 
                                      null=True, blank=True)
    excerpt = models.TextField(_('Excerpt'), max_length=300, blank=True, 
                              help_text=_('Brief summary of the article (max 300 characters)'))
    
    # العلاقات
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, 
                                related_name='articles', verbose_name=_('Category'))
    tags = models.ManyToManyField(Tag, blank=True, verbose_name=_('Tags'))
    related_articles = models.ManyToManyField('self', blank=True, symmetrical=False, 
                                             verbose_name=_('Related Articles'))
    
    # الإعدادات
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='draft')
    is_featured = models.BooleanField(_('Is Featured'), default=False)
    is_pinned = models.BooleanField(_('Is Pinned'), default=False, 
                                   help_text=_('Pin this article to the top of lists'))
    allow_comments = models.BooleanField(_('Allow Comments'), default=True)
    is_premium = models.BooleanField(_('Premium Content'), default=False, 
                                    help_text=_('This article is for premium users only'))
    
    # SEO
    meta_title = models.CharField(_('Meta Title'), max_length=70, blank=True, 
                                 help_text=_('Title for SEO (max 70 characters)'))
    meta_description = models.CharField(_('Meta Description'), max_length=160, blank=True, 
                                       help_text=_('Description for SEO (max 160 characters)'))
    
    # التواريخ
    published_at = models.DateTimeField(_('Published At'), null=True, blank=True)
    scheduled_for = models.DateTimeField(_('Scheduled For'), null=True, blank=True, 
                                        help_text=_('Schedule publication for a future date'))
    
    class Meta:
        verbose_name = _('Article')
        verbose_name_plural = _('Articles')
        ordering = ['-is_pinned', '-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['is_featured', 'status']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        # إذا تم نشر المقال لأول مرة، ضع تاريخ النشر
        if self.status == 'published' and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()
        
        # إذا كان المقال محدد للنشر في وقت لاحق
        if self.scheduled_for and self.scheduled_for <= timezone.now():
            self.status = 'published'
            self.published_at = self.scheduled_for
        
        # إذا كان عنوان الـ Meta فارغاً، استخدم العنوان العادي
        if not self.meta_title:
            self.meta_title = self.title[:70]
        
        # إذا كان وصف الـ Meta فارغاً، استخدم الملخص
        if not self.meta_description and self.excerpt:
            self.meta_description = self.excerpt[:160]
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('articles:detail', kwargs={'slug': self.slug})
    
    def is_published(self):
        """التحقق إذا كان المقال منشور"""
        return self.status == 'published'
    
    def get_reading_time_text(self):
        """نص وقت القراءة"""
        if self.reading_time == 1:
            return _('1 minute read')
        return f'{self.reading_time} {_("minutes read")}'
    
    def increment_views(self):
        """زيادة عدد المشاهدات"""
        self.views += 1
        self.save(update_fields=['views'])
    
    def get_related_articles_with_fallback(self, count=3):
        """الحصول على مقالات ذات صلة مع خيار احتياطي"""
        related = self.related_articles.filter(status='published')
        
        if related.count() >= count:
            return related[:count]
        
        # إذا لم يكن هناك مقالات مرتبطة كافية، أضف مقالات من نفس التصنيف
        same_category = Article.objects.filter(
            category=self.category,
            status='published'
        ).exclude(id=self.id).distinct()
        
        result = list(related)
        needed = count - len(result)
        
        if needed > 0 and same_category.exists():
            # استبعاد المقالات المضافة بالفعل
            existing_ids = [article.id for article in result]
            additional = same_category.exclude(id__in=existing_ids)[:needed]
            result.extend(additional)
        
        return result[:count]
    
    @property
    def comments_count(self):
        """عدد التعليقات المعتمدة"""
        return self.comments.filter(is_approved=True).count()

class Comment(models.Model):
    """نموذج التعليقات على المقالات"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, 
                               related_name='comments', verbose_name=_('Article'))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                              related_name='replies', verbose_name=_('Parent Comment'))
    
    # معلومات المستخدم
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(_('Name'), max_length=100)
    email = models.EmailField(_('Email'))
    website = models.URLField(_('Website'), blank=True)
    
    # المحتوى
    content = models.TextField(_('Comment'))
    
    # الحالة
    is_approved = models.BooleanField(_('Is Approved'), default=False)
    is_spam = models.BooleanField(_('Is Spam'), default=False)
    is_edited = models.BooleanField(_('Is Edited'), default=False)
    
    # التقييم
    likes = models.PositiveIntegerField(_('Likes'), default=0)
    dislikes = models.PositiveIntegerField(_('Dislikes'), default=0)
    
    # التواريخ
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
        
    # تتبع
    ip_address = models.GenericIPAddressField(_('IP Address'), null=True, blank=True)
    user_agent = models.TextField(_('User Agent'), blank=True)
    
    class Meta:
        verbose_name = _('Comment')
        verbose_name_plural = _('Comments')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Comment by {self.name} on {self.article.title}"
    
    def get_absolute_url(self):
        return f"{self.article.get_absolute_url()}#comment-{self.id}"
    
    def is_reply(self):
        """التحقق إذا كان التعليق رداً"""
        return self.parent is not None
    
    def get_replies(self):
        """الحصول على الردود"""
        return self.replies.filter(is_approved=True, is_spam=False)
    
    def get_vote_score(self):
        """حساب نتيجة التصويت"""
        return self.likes - self.dislikes
    
    def approve(self):
        """اعتماد التعليق"""
        self.is_approved = True
        self.save()
    
    def mark_as_spam(self):
        """وضع علامة كسبام"""
        self.is_spam = True
        self.save()

# نماذج إضافية
class ArticleView(models.Model):
    """تتبع مشاهدات المقالات"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='article_views')
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    session_key = models.CharField(max_length=40)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
        
    class Meta:
        verbose_name = _('Article View')
        verbose_name_plural = _('Article Views')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['article', 'created_at']),
            models.Index(fields=['ip_address', 'session_key']),
        ]
    
    def __str__(self):
        return f"View of {self.article.title}"

class ArticleRating(models.Model):
    """تقييمات المقالات"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(_('Rating'), choices=[(i, str(i)) for i in range(1, 6)])
    ip_address = models.GenericIPAddressField()
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
        
    class Meta:
        verbose_name = _('Article Rating')
        verbose_name_plural = _('Article Ratings')
        unique_together = [['article', 'user'], ['article', 'ip_address']]
    
    def __str__(self):
        return f"Rating {self.rating} for {self.article.title}"

class Bookmark(models.Model):
    """المقالات المفضلة للمستخدمين"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='bookmarked_by')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
        
    class Meta:
        verbose_name = _('Bookmark')
        verbose_name_plural = _('Bookmarks')
        unique_together = ['user', 'article']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} bookmarked {self.article.title}"
