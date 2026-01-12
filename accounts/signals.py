from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Group
from .models import CustomUser

@receiver(post_save, sender=CustomUser)
def assign_user_group(sender, instance, created, **kwargs):
    """تعيين المستخدم للمجموعة المناسبة حسب نوعه"""
    if created:
        group_name = None
        
        if instance.user_type == 'admin':
            group_name = 'Administrators'
        elif instance.user_type == 'editor':
            group_name = 'Editors'
        elif instance.user_type == 'user':
            group_name = 'Users'
        
        if group_name:
            try:
                group = Group.objects.get(name=group_name)
                instance.groups.add(group)
            except Group.DoesNotExist:
                # إنشاء المجموعة إذا لم تكن موجودة
                group = Group.objects.create(name=group_name)
                instance.groups.add(group)

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    """إنشاء ملف شخصي افتراضي للمستخدم"""
    if created and not instance.profile_picture:
        # يمكنك إضافة منطق لتعيين صورة افتراضية هنا
        pass