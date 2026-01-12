from django.db import models
from django.utils.translation import gettext_lazy as _
from core.models import BaseContent

class Scholarship(BaseContent):
    TYPE_CHOICES = [
        ('undergraduate', _('Undergraduate')),
        ('masters', _('Master\'s')),
        ('phd', _('PhD')),
        ('postdoc', _('Postdoctoral')),
        ('research', _('Research')),
    ]
    
    scholarship_type = models.CharField(_('Type'), max_length=20, choices=TYPE_CHOICES)
    country = models.CharField(_('Country'), max_length=100)
    university = models.CharField(_('University/Institution'), max_length=200)
    deadline = models.DateField(_('Application Deadline'))
    funding_amount = models.TextField(_('Funding Amount'), blank=True)
    eligibility = models.TextField(_('Eligibility Criteria'))
    application_process = models.TextField(_('Application Process'))
    official_link = models.URLField(_('Official Link'))
    is_featured = models.BooleanField(_('Featured Scholarship'), default=False)
    
    class Meta:
        verbose_name = _('Scholarship')
        verbose_name_plural = _('Scholarships')
    
    @property
    def is_deadline_passed(self):
        from django.utils import timezone
        return self.deadline < timezone.now().date()
    
    @property
    def days_until_deadline(self):
        from django.utils import timezone
        delta = self.deadline - timezone.now().date()
        return delta.days if delta.days > 0 else 0

class ApplicationTip(models.Model):
    scholarship = models.ForeignKey(Scholarship, on_delete=models.CASCADE, related_name='tips')
    title = models.CharField(_('Tip Title'), max_length=200)
    content = models.TextField(_('Tip Content'))
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return self.title