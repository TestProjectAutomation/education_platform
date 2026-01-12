from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Article, Comment, Category, Tag
from django.utils import timezone

class ArticleForm(forms.ModelForm):
    """نموذج إنشاء/تعديل مقال"""
    
    class Meta:
        model = Article
        fields = [
            'title', 'slug', 'content', 'excerpt', 'featured_image',
            'category', 'tags', 'reading_time', 'status',
            'is_featured', 'is_pinned', 'is_premium', 'allow_comments',
            'meta_title', 'meta_description', 'scheduled_for'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Enter article title')
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('auto-generated-from-title')
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 15,
                'placeholder': _('Write your article content here...')
            }),
            'excerpt': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': _('Brief summary of the article (max 300 characters)')
            }),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control', 'data-placeholder': _('Select tags')}),
            'reading_time': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 60
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_premium': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'allow_comments': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'meta_title': forms.TextInput(attrs={
                'class': 'form-control',
                'maxlength': '70',
                'placeholder': _('SEO title (max 70 characters)')
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'maxlength': '160',
                'placeholder': _('SEO description (max 160 characters)')
            }),
            'scheduled_for': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local',
                'min': timezone.now().strftime('%Y-%m-%dT%H:%M')
            }),
        }
    
    def clean_meta_title(self):
        meta_title = self.cleaned_data.get('meta_title')
        if meta_title and len(meta_title) > 70:
            raise forms.ValidationError(_('Meta title cannot exceed 70 characters.'))
        return meta_title
    
    def clean_meta_description(self):
        meta_description = self.cleaned_data.get('meta_description')
        if meta_description and len(meta_description) > 160:
            raise forms.ValidationError(_('Meta description cannot exceed 160 characters.'))
        return meta_description
    
    def clean_scheduled_for(self):
        scheduled_for = self.cleaned_data.get('scheduled_for')
        if scheduled_for and scheduled_for <= timezone.now():
            raise forms.ValidationError(_('Scheduled time must be in the future.'))
        return scheduled_for

class CommentForm(forms.ModelForm):
    """نموذج التعليقات"""
    
    class Meta:
        model = Comment
        fields = ['name', 'email', 'website', 'content']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': _('Your name')
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': _('Your email')
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': _('Your website (optional)')
            }),
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': _('Your comment...')
            }),
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content) < 10:
            raise forms.ValidationError(_('Comment must be at least 10 characters long.'))
        if len(content) > 1000:
            raise forms.ValidationError(_('Comment cannot exceed 1000 characters.'))
        return content

class ArticleFilterForm(forms.Form):
    """نموذج تصفية المقالات"""
    
    SORT_CHOICES = [
        ('-published_at', _('Newest First')),
        ('published_at', _('Oldest First')),
        ('-views', _('Most Viewed')),
        ('title', _('Title A-Z')),
        ('-title', _('Title Z-A')),
        ('rating', _('Highest Rated')),
        ('comments', _('Most Comments')),
    ]
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Search articles...')
        })
    )
    
    category = forms.ModelChoiceField(
        queryset=Category.objects.filter(is_active=True),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        required=False,
        widget=forms.SelectMultiple(attrs={'class': 'form-control', 'data-placeholder': _('Select tags')})
    )
    
    author = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': _('Author username')
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    sort_by = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    show_featured = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    show_premium = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get('date_from')
        date_to = cleaned_data.get('date_to')
        
        if date_from and date_to and date_from > date_to:
            self.add_error('date_to', _('End date must be after start date.'))
        
        return cleaned_data
