from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.core.cache import cache
from django.contrib.auth.models import User
from .models import Page, PageComment

@receiver(post_save, sender=Page)
def clear_page_cache(sender, instance, **kwargs):
    """Clear cache when page is saved"""
    # Clear detail page cache
    cache_key = f'page_detail_{instance.slug}_*'
    cache.delete_pattern(cache_key)
    
    # Clear list page cache
    cache.delete('page_list')
    
    # Clear sitemap cache
    cache.delete('pages_sitemap')

@receiver(pre_delete, sender=Page)
def clear_cache_on_delete(sender, instance, **kwargs):
    """Clear cache when page is deleted"""
    cache_key = f'page_detail_{instance.slug}_*'
    cache.delete_pattern(cache_key)
    cache.delete('page_list')
    cache.delete('pages_sitemap')

@receiver(post_save, sender=PageComment)
def send_comment_notification(sender, instance, created, **kwargs):
    """Send email notification for new comments"""
    if created and instance.is_approved:
        # Send notification to page author
        page_author = instance.page.author
        if page_author and page_author.email:
            from django.core.mail import send_mail
            from django.template.loader import render_to_string
            from django.utils.html import strip_tags
            
            subject = f'New comment on your page: {instance.page.title}'
            html_message = render_to_string('emails/comment_notification.html', {
                'comment': instance,
                'page': instance.page
            })
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email='noreply@example.com',
                recipient_list=[page_author.email],
                html_message=html_message,
                fail_silently=True
            )