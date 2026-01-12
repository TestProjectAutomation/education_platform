# accounts/models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
import os

def profile_picture_upload_path(instance, filename):
    """Generate upload path for profile pictures"""
    ext = filename.split('.')[-1]
    filename = f"{instance.username}_profile.{ext}"
    return os.path.join('profile_pics', str(instance.id), filename)

class CustomUser(AbstractUser):
    USER_TYPE_CHOICES = (
        ('admin', _('Admin')),
        ('editor', _('Editor')),
        ('instructor', _('Instructor')),
        ('student', _('Student')),
        ('user', _('User')),
    )
    
    user_type = models.CharField(
        max_length=20, 
        choices=USER_TYPE_CHOICES, 
        default='user'
    )
    profile_picture = models.ImageField(
        upload_to=profile_picture_upload_path, 
        null=True, 
        blank=True,
        verbose_name=_('Profile Picture')
    )
    bio = models.TextField(
        _('Bio'), 
        blank=True,
        help_text=_('Tell us about yourself')
    )
    phone = models.CharField(
        max_length=20, 
        blank=True,
        validators=[
            RegexValidator(
                regex=r'^\+?1?\d{9,15}$',
                message=_("Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.")
            )
        ]
    )
    facebook_url = models.URLField(blank=True, verbose_name=_('Facebook URL'))
    twitter_url = models.URLField(blank=True, verbose_name=_('Twitter URL'))
    linkedin_url = models.URLField(blank=True, verbose_name=_('LinkedIn URL'))
    dark_mode = models.BooleanField(default=False)
    email_verified = models.BooleanField(default=False)
    phone_verified = models.BooleanField(default=False)
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_('Date of Birth'))
    country = models.CharField(max_length=100, blank=True, verbose_name=_('Country'))
    city = models.CharField(max_length=100, blank=True, verbose_name=_('City'))
    address = models.TextField(blank=True, verbose_name=_('Address'))
    
    # Points and achievements
    points = models.IntegerField(default=0)
    level = models.IntegerField(default=1)
    experience = models.IntegerField(default=0)
    
    # Social fields
    website = models.URLField(blank=True, verbose_name=_('Website'))
    github_url = models.URLField(blank=True, verbose_name=_('GitHub URL'))
    youtube_url = models.URLField(blank=True, verbose_name=_('YouTube URL'))
    
    # Preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    newsletter_subscription = models.BooleanField(default=True)
    
    # Timestamps
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['user_type']),
            models.Index(fields=['points']),
        ]
    
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        """Return the full name of the user"""
        full_name = f"{self.first_name} {self.last_name}"
        return full_name.strip() if full_name.strip() else self.username
    
    def get_display_name(self):
        """Return display name (full name or username)"""
        if self.first_name and self.last_name:
            return self.get_full_name()
        return self.username
    
    def get_initials(self):
        """Get user initials for avatar"""
        if self.first_name and self.last_name:
            return f"{self.first_name[0]}{self.last_name[0]}".upper()
        elif self.first_name:
            return self.first_name[0].upper()
        elif self.last_name:
            return self.last_name[0].upper()
        else:
            return self.username[0].upper() if self.username else 'U'
    
    def get_profile_picture_url(self):
        """Return profile picture URL or default"""
        if self.profile_picture and hasattr(self.profile_picture, 'url'):
            return self.profile_picture.url
        return '/static/images/default-avatar.png'
    
    def add_points(self, points):
        """Add points to user and check for level up"""
        self.points += points
        self.experience += points
        
        # Simple leveling system (1000 points per level)
        new_level = (self.experience // 1000) + 1
        if new_level > self.level:
            self.level = new_level
        
        self.save()
    
    def has_completed_profile(self):
        """Check if user has completed their profile"""
        required_fields = ['first_name', 'last_name', 'email', 'phone']
        for field in required_fields:
            if not getattr(self, field):
                return False
        return True
    
    def profile_completion_percentage(self):
        """Calculate profile completion percentage"""
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'bio', 'profile_picture', 'country', 'city'
        ]
        completed = 0
        
        for field in fields:
            if getattr(self, field):
                completed += 1
        
        return int((completed / len(fields)) * 100)
    
    def clean(self):
        """Custom validation"""
        super().clean()
        
        # Ensure email is unique
        if self.email:
            if CustomUser.objects.filter(email=self.email).exclude(id=self.id).exists():
                raise ValidationError({'email': _('This email is already registered.')})
        
        # Validate phone number
        if self.phone and not self.phone.startswith('+'):
            # Add country code if missing
            self.phone = f"+20{self.phone.lstrip('0')}"

# Related Models

class UserActivity(models.Model):
    ACTIVITY_TYPES = (
        ('login', _('Login')),
        ('logout', _('Logout')),
        ('course_enroll', _('Course Enrollment')),
        ('course_complete', _('Course Completion')),
        ('profile_update', _('Profile Update')),
        ('comment', _('Comment')),
        ('like', _('Like')),
        ('share', _('Share')),
        ('certificate', _('Certificate Earned')),
        ('achievement', _('Achievement Unlocked')),
    )
    
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='activities'
    )
    activity_type = models.CharField(
        max_length=50, 
        choices=ACTIVITY_TYPES
    )
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('User Activity')
        verbose_name_plural = _('User Activities')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['activity_type']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"

class UserNotification(models.Model):
    NOTIFICATION_TYPES = (
        ('info', _('Information')),
        ('success', _('Success')),
        ('warning', _('Warning')),
        ('error', _('Error')),
        ('course', _('Course Update')),
        ('system', _('System')),
    )
    
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='notifications'
    )
    notification_type = models.CharField(
        max_length=20, 
        choices=NOTIFICATION_TYPES,
        default='info'
    )
    title = models.CharField(max_length=200)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    action_url = models.URLField(blank=True)
    icon = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return self.title
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save()

class Achievement(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='fas fa-trophy')
    points = models.IntegerField(default=100)
    requirements = models.JSONField(default=dict, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Achievement')
        verbose_name_plural = _('Achievements')
        ordering = ['-points']
    
    def __str__(self):
        return self.name

class UserAchievement(models.Model):
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='user_achievements'
    )
    achievement = models.ForeignKey(
        Achievement, 
        on_delete=models.CASCADE
    )
    unlocked_at = models.DateTimeField(auto_now_add=True)
    progress = models.IntegerField(default=0)
    is_unlocked = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = _('User Achievement')
        verbose_name_plural = _('User Achievements')
        unique_together = ['user', 'achievement']
        ordering = ['-unlocked_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"

class LearningGoal(models.Model):
    GOAL_STATUS = (
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('paused', _('Paused')),
    )
    
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='learning_goals'
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    target_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20, 
        choices=GOAL_STATUS,
        default='active'
    )
    progress = models.IntegerField(default=0)
    total_items = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Learning Goal')
        verbose_name_plural = _('Learning Goals')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
        ]
    
    def __str__(self):
        return self.title
    
    def progress_percentage(self):
        if self.total_items == 0:
            return 0
        return int((self.progress / self.total_items) * 100)
    
    def is_overdue(self):
        if self.target_date:
            from django.utils.timezone import now
            return now().date() > self.target_date
        return False

class Bookmark(models.Model):
    CONTENT_TYPES = (
        ('course', _('Course')),
        ('lesson', _('Lesson')),
        ('article', _('Article')),
        ('video', _('Video')),
        ('quiz', _('Quiz')),
    )
    
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE,
        related_name='bookmarks'
    )
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    object_id = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    url = models.URLField()
    thumbnail = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Bookmark')
        verbose_name_plural = _('Bookmarks')
        unique_together = ['user', 'content_type', 'object_id']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"