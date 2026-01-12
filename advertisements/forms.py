from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Advertisement, AdPlacement

class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = [
            'title', 'placement', 'ad_type', 'image', 'text_content',
            'html_code', 'video_url', 'link', 'start_date', 'end_date',
            'active'
        ]
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'text_content': forms.Textarea(attrs={'rows': 4}),
            'html_code': forms.Textarea(attrs={'rows': 6}),
        }

class AdPlacementForm(forms.ModelForm):
    class Meta:
        model = AdPlacement
        fields = ['name', 'code', 'placement_type', 'description', 'width', 'height', 'active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }