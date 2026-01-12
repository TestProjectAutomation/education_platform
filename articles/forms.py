from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Article, Comment

class ArticleForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = [
            'title', 'slug', 'content', 'excerpt', 'featured_image',
            'categories', 'tags', 'status', 'reading_time',
            'link_display_duration', 'is_featured'
        ]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'excerpt': forms.Textarea(attrs={'rows': 3}),
        }

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['name', 'email', 'content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': _('Write your comment here...')
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'placeholder': _('Your name')})
        self.fields['email'].widget.attrs.update({'placeholder': _('Your email')})