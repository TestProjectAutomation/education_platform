from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Article, Comment
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

@receiver(pre_save, sender=Article)
def handle_article_scheduling(sender, instance, **kwargs):
    """معالجة جدولة المقالات"""
    if instance.scheduled_for and instance.scheduled_for <= timezone.now():
        instance.status = 'published'
        instance.published_at = instance.scheduled_for
        logger.info(f"Article {instance.title} published as scheduled.")

@receiver(post_save, sender=Article)
def clear_article_cache(sender, instance, **kwargs):
    """مسح كاش المقالات عند التحديث"""
    # مسح كاش الصفحات الرئيسية
    cache_keys = [
        'article_list_*',
        'article_featured_*',
        'article_popular_*',
        'article_tag_*',
        'article_category_*',
    ]
    
    for key_pattern in cache_keys:
        cache.delete_pattern(key_pattern)
    
    logger.info(f"Article cache cleared for {instance.title}")

@receiver(post_save, sender=Comment)
def handle_new_comment(sender, instance, created, **kwargs):
    """معالجة التعليقات الجديدة"""
    if created and instance.is_approved:
        # زيادة عداد التعليقات في المقال
        instance.article.save()
        
        # إرسال إشعار للمؤلف إذا كان مختلفاً عن صاحب التعليق
        if instance.user and instance.user != instance.article.author:
            from django.core.mail import send_mail
            from django.template.loader import render_to_string
            
            subject = _('New comment on your article: {title}').format(
                title=instance.article.title
            )
            
            message = render_to_string('emails/new_comment_author.html', {
                'comment': instance,
                'article': instance.article,
            })
            
            send_mail(
                subject,
                message,
                'noreply@example.com',
                [instance.article.author.email],
                html_message=message,
                fail_silently=True
            )
        
        logger.info(f"New comment added to article {instance.article.title}")

@receiver(pre_save, sender=Comment)
def check_comment_spam(sender, instance, **kwargs):
    """فحص التعليقات للكشف عن السبام"""
    spam_keywords = ['viagra', 'casino', 'porn', 'buy now', 'click here', 'make money']
    
    content_lower = instance.content.lower()
    
    # فحص المحتوى
    for keyword in spam_keywords:
        if keyword in content_lower:
            instance.is_spam = True
            instance.is_approved = False
            logger.warning(f"Comment marked as spam: {instance.content[:50]}...")
            break
    
    # فحص الروابط المفرطة
    if content_lower.count('http') > 3:
        instance.is_spam = True
        instance.is_approved = False
        logger.warning(f"Comment marked as spam (too many links): {instance.content[:50]}...")