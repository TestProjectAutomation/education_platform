from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from ckeditor.widgets import CKEditorWidget
from .models import Page, PageComment, PageRating
import datetime

class PageForm(forms.ModelForm):
    content = forms.CharField(widget=CKEditorWidget(config_name='default'))
    excerpt = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3, 'maxlength': 500}),
        required=False,
        help_text=_('Maximum 500 characters')
    )
    publish_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False
    )
    expire_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        required=False
    )
    
    class Meta:
        model = Page
        fields = [
            'title', 'slug', 'content', 'excerpt', 
            'featured_image', 'thumbnail', 'template', 
            'status', 'order', 'show_in_menu', 'show_in_sitemap',
            'parent', 'author', 'allow_comments',
            'seo_title', 'seo_description', 'seo_keywords',
            'canonical_url', 'publish_date', 'expire_date'
        ]
        widgets = {
            'seo_description': forms.Textarea(attrs={'rows': 3, 'maxlength': 300}),
            'seo_keywords': forms.TextInput(attrs={'placeholder': _('keyword1, keyword2, keyword3')}),
            'order': forms.NumberInput(attrs={'min': 0}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user and not user.is_superuser:
            # Limit parent selection for non-superusers
            self.fields['parent'].queryset = Page.objects.filter(
                status='published'
            )
        
        # Set current user as author if not set
        if user and not self.instance.pk:
            self.initial['author'] = user
    
    def clean(self):
        cleaned_data = super().clean()
        publish_date = cleaned_data.get('publish_date')
        expire_date = cleaned_data.get('expire_date')
        
        if publish_date and expire_date and publish_date >= expire_date:
            self.add_error('expire_date', _('Expire date must be after publish date'))
        
        # Auto-generate slug if empty
        if not cleaned_data.get('slug') and cleaned_data.get('title'):
            from django.utils.text import slugify
            cleaned_data['slug'] = slugify(cleaned_data['title'])
        
        return cleaned_data


class PageCommentForm(forms.ModelForm):
    class Meta:
        model = PageComment
        fields = ['content', 'parent']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': _('Write your comment here...'),
                'class': 'form-control'
            }),
            'parent': forms.HiddenInput(),
        }


class PageRatingForm(forms.ModelForm):
    class Meta:
        model = PageRating
        fields = ['rating']
        widgets = {
            'rating': forms.RadioSelect(choices=[
                (1, '★'),
                (2, '★★'),
                (3, '★★★'),
                (4, '★★★★'),
                (5, '★★★★★'),
            ])
        }


class PageSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': _('Search pages...'),
            'class': 'form-control'
        })
    )
    
    category = forms.ChoiceField(
        required=False,
        choices=[('', _('All Categories'))],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically add categories
        from .models import Page
        categories = Page.objects.filter(
            parent__isnull=True,
            status='published'
        ).values_list('id', 'title')
        self.fields['category'].choices = [('', _('All Categories'))] + list(categories)