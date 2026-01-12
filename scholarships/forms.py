from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Scholarship, ApplicationTip

class ScholarshipForm(forms.ModelForm):
    class Meta:
        model = Scholarship
        fields = [
            'title', 'slug', 'content', 'excerpt', 'featured_image',
            'categories', 'scholarship_type', 'country', 'university',
            'deadline', 'funding_amount', 'eligibility', 'application_process',
            'official_link', 'link_display_duration', 'is_featured', 'status'
        ]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 12}),
            'excerpt': forms.Textarea(attrs={'rows': 3}),
            'eligibility': forms.Textarea(attrs={'rows': 6}),
            'application_process': forms.Textarea(attrs={'rows': 6}),
            'funding_amount': forms.Textarea(attrs={'rows': 3}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

class ApplicationTipForm(forms.ModelForm):
    class Meta:
        model = ApplicationTip
        fields = ['title', 'content', 'order']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }