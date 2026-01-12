from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import UserNotification

User = get_user_model()

@receiver(post_save, sender=User)
def send_welcome_notification(sender, instance, created, **kwargs):
    """Send welcome notification when new user is created"""
    if created:
        UserNotification.objects.create(
            user=instance,
            notification_type='success',
            title='Welcome to our platform!',
            message='Thank you for joining us. Start your learning journey now!',
            icon='fas fa-heart',
            action_url='/dashboard/'
        )