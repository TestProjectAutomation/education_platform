from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseContent

class Course(BaseContent):
    LEVEL_CHOICES = [
        ('beginner', _('Beginner')),
        ('intermediate', _('Intermediate')),
        ('advanced', _('Advanced')),
    ]
    
    price = models.DecimalField(_('Price'), max_digits=10, decimal_places=2, default=0)
    discount_price = models.DecimalField(_('Discount Price'), max_digits=10, decimal_places=2, null=True, blank=True)
    duration = models.CharField(_('Duration'), max_length=100)
    level = models.CharField(_('Level'), max_length=20, choices=LEVEL_CHOICES, default='beginner')
    instructor = models.CharField(_('Instructor'), max_length=200)
    is_featured = models.BooleanField(_('Featured'), default=False)
    enrollment_count = models.PositiveIntegerField(_('Enrollments'), default=0)
    requirements = models.TextField(_('Requirements'), blank=True)
    what_you_will_learn = models.TextField(_('What You Will Learn'), blank=True)
    
    class Meta:
        verbose_name = _('Course')
        verbose_name_plural = _('Courses')
    
    @property
    def current_price(self):
        return self.discount_price if self.discount_price else self.price
    
    @property
    def has_discount(self):
        return self.discount_price is not None
    
    def increment_enrollment(self):
        self.enrollment_count += 1
        self.save(update_fields=['enrollment_count'])

class CourseModule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(_('Title'), max_length=200)
    order = models.IntegerField(default=0)
    description = models.TextField(_('Description'), blank=True)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.course.title} - {self.title}"

class CourseLesson(models.Model):
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(_('Title'), max_length=200)
    video_url = models.URLField(_('Video URL'), blank=True)
    content = models.TextField(_('Content'), blank=True)
    duration = models.PositiveIntegerField(_('Duration in minutes'), default=0)
    order = models.IntegerField(default=0)
    is_free = models.BooleanField(_('Free Lesson'), default=False)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title

class Enrollment(models.Model):
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'course']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"

class Review(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey('accounts.CustomUser', on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(
        _('Rating'),
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    comment = models.TextField(_('Comment'), blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['course', 'user']
    
    def __str__(self):
        return f"{self.user.username} - {self.course.title}"