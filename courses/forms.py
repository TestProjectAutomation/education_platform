from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Course, Review

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = [
            'title', 'slug', 'content', 'excerpt', 'featured_image',
            'categories', 'price', 'discount_price', 'duration',
            'level', 'instructor', 'requirements', 'what_you_will_learn',
            'link_display_duration', 'is_featured', 'status'
        ]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'excerpt': forms.Textarea(attrs={'rows': 3}),
            'requirements': forms.Textarea(attrs={'rows': 4}),
            'what_you_will_learn': forms.Textarea(attrs={'rows': 6}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': _('Share your experience with this course...')
            }),
        }