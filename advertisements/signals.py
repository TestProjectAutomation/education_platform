from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache
from .models import Advertisement, AdPlacement

@receiver([post_save, post_delete], sender=Advertisement)
@receiver([post_save, post_delete], sender=AdPlacement)
def clear_ad_cache(sender, **kwargs):
    """مسح كاش الإعلانات عند التحديث"""
    cache.delete_pattern('active_ads_*')

@receiver(pre_save, sender=Advertisement)
def validate_ad_dates(sender, instance, **kwargs):
    """التحقق من صحة التواريخ"""
    if instance.start_date and instance.end_date:
        if instance.start_date >= instance.end_date:
            raise ValueError("Start date must be before end date")