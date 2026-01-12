from django import forms
from django.utils.translation import gettext_lazy as _
from ckeditor.widgets import CKEditorWidget
from .models import Page

class PageForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget())
    
    class Meta:
        model = Page
        fields = [
            'title', 'slug', 'content', 'excerpt', 'featured_image',
            'template', 'status', 'order', 'show_in_menu', 'parent',
            'seo_title', 'seo_description'
        ]
        widgets = {
            'excerpt': forms.Textarea(attrs={'rows': 3}),
            'seo_description': forms.Textarea(attrs={'rows': 3}),
        }