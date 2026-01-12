from django import forms
from django.utils.translation import gettext_lazy as _


class SiteSettingForm(forms.ModelForm):
    """Form for site settings"""
    
    class Meta:
        # We'll specify the model later to avoid circular import
        fields = [
            'site_name',
            'site_description',
            'logo',
            'favicon',
            'contact_email',
            'facebook_url',
            'twitter_url',
            'linkedin_url',
            'instagram_url',
            'youtube_url',
            'default_language',
            'maintenance_mode'
        ]
        widgets = {
            'site_name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': _('Enter site name')
            }),
            'site_description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': _('Enter site description')
            }),
            'contact_email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'contact@example.com'
            }),
            'facebook_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://facebook.com/yourpage'
            }),
            'twitter_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://twitter.com/yourprofile'
            }),
            'linkedin_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://linkedin.com/company/yourcompany'
            }),
            'instagram_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://instagram.com/yourprofile'
            }),
            'youtube_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://youtube.com/c/yourchannel'
            }),
            'default_language': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('ar', _('Arabic')),
                ('en', _('English')),
                ('fr', _('French')),
                ('es', _('Spanish'))
            ]),
            'maintenance_mode': forms.CheckboxInput(attrs={'class': 'form-checkbox h-5 w-5 text-primary-600'})
        }
        labels = {
            'site_name': _('Site Name'),
            'site_description': _('Site Description'),
            'logo': _('Logo'),
            'favicon': _('Favicon'),
            'contact_email': _('Contact Email'),
            'facebook_url': _('Facebook URL'),
            'twitter_url': _('Twitter URL'),
            'linkedin_url': _('LinkedIn URL'),
            'instagram_url': _('Instagram URL'),
            'youtube_url': _('YouTube URL'),
            'default_language': _('Default Language'),
            'maintenance_mode': _('Maintenance Mode')
        }
        help_texts = {
            'site_description': _('A brief description of your site for SEO'),
            'logo': _('Recommended size: 200x50 pixels'),
            'favicon': _('Recommended size: 32x32 or 64x64 pixels'),
            'maintenance_mode': _('When enabled, only admins can access the site')
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add custom validation or styling
        for field_name, field in self.fields.items():
            if field_name not in ['maintenance_mode']:
                field.widget.attrs.update({'class': 'form-input'})
            
            # Make file fields more user-friendly
            if field_name in ['logo', 'favicon']:
                field.widget.attrs.update({'class': 'file-input'})


class CategoryForm(forms.ModelForm):
    """Form for categories"""
    
    class Meta:
        # We'll specify the model later to avoid circular import
        fields = ['name', 'slug', 'description', 'icon', 'order']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': _('Enter category name')
            }),
            'slug': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': _('Enter URL slug')
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': _('Enter category description (optional)')
            }),
            'icon': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'fas fa-category'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0'
            })
        }
        labels = {
            'name': _('Category Name'),
            'slug': _('URL Slug'),
            'description': _('Description'),
            'icon': _('Icon Class'),
            'order': _('Display Order')
        }
        help_texts = {
            'slug': _('Used in URLs. Use lowercase letters, numbers, and hyphens'),
            'icon': _('Font Awesome icon class (e.g., fas fa-category)'),
            'order': _('Lower numbers appear first')
        }
    
    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if not slug:
            from django.utils.text import slugify
            slug = slugify(self.cleaned_data.get('name'))
        return slug


class ContactForm(forms.Form):
    """Contact form for the website"""
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': _('Your Name')
        }),
        label=_('Name')
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'email@example.com'
        }),
        label=_('Email')
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': _('Subject')
        }),
        label=_('Subject')
    )
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 5,
            'placeholder': _('Your Message')
        }),
        label=_('Message')
    )
    
    def clean_message(self):
        message = self.cleaned_data.get('message')
        if len(message.strip()) < 10:
            raise forms.ValidationError(_('Please enter a more detailed message.'))
        return message


class NewsletterSubscriptionForm(forms.Form):
    """Newsletter subscription form"""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'email@example.com',
            'aria-label': _('Email address')
        }),
        label=_('Email Address')
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        # You could add validation for existing subscriptions here
        return email


class SearchForm(forms.Form):
    """Search form for the site"""
    query = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': _('Search...'),
            'aria-label': _('Search')
        }),
        label=_('Search'),
        required=False
    )
    category = forms.ChoiceField(
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Category'),
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Dynamically populate categories
        from .models import Category
        categories = Category.objects.all()
        category_choices = [('', _('All Categories'))]
        category_choices.extend([(cat.id, cat.name) for cat in categories])
        self.fields['category'].choices = category_choices


class AdvancedSettingsForm(forms.Form):
    """Advanced site settings form"""
    analytics_code = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-input font-mono text-sm',
            'rows': 4,
            'placeholder': '<!-- Google Analytics or other tracking code -->'
        }),
        label=_('Analytics Code'),
        required=False,
        help_text=_('Paste your analytics tracking code (e.g., Google Analytics)')
    )
    
    custom_css = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-input font-mono text-sm',
            'rows': 6,
            'placeholder': '/* Add custom CSS here */'
        }),
        label=_('Custom CSS'),
        required=False,
        help_text=_('Add custom CSS styles to override default styles')
    )
    
    custom_js = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-input font-mono text-sm',
            'rows': 6,
            'placeholder': '// Add custom JavaScript here'
        }),
        label=_('Custom JavaScript'),
        required=False,
        help_text=_('Add custom JavaScript code')
    )
    
    meta_tags = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-input font-mono text-sm',
            'rows': 4,
            'placeholder': '<meta name="keywords" content="your, keywords, here">'
        }),
        label=_('Additional Meta Tags'),
        required=False,
        help_text=_('Add additional meta tags for SEO')
    )


class ContentImportForm(forms.Form):
    """Form for importing content"""
    IMPORT_CHOICES = [
        ('csv', 'CSV File'),
        ('json', 'JSON File'),
        ('excel', 'Excel File'),
    ]
    
    CONTENT_TYPE_CHOICES = [
        ('articles', 'Articles'),
        ('courses', 'Courses'),
        ('books', 'Books'),
        ('scholarships', 'Scholarships'),
    ]
    
    import_type = forms.ChoiceField(
        choices=IMPORT_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-radio'}),
        label=_('Import Format'),
        initial='csv'
    )
    
    content_type = forms.ChoiceField(
        choices=CONTENT_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Content Type')
    )
    
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'file-input',
            'accept': '.csv,.json,.xlsx,.xls'
        }),
        label=_('File'),
        help_text=_('Upload CSV, JSON, or Excel file')
    )
    
    overwrite = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        label=_('Overwrite existing content'),
        help_text=_('If checked, existing content with the same slug will be overwritten')
    )
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            import os
            ext = os.path.splitext(file.name)[1].lower()
            if ext not in ['.csv', '.json', '.xlsx', '.xls']:
                raise forms.ValidationError(_('Unsupported file format. Please upload CSV, JSON, or Excel file.'))
            # Check file size (10MB limit)
            if file.size > 10 * 1024 * 1024:
                raise forms.ValidationError(_('File size should not exceed 10MB.'))
        return file


class ContentExportForm(forms.Form):
    """Form for exporting content"""
    EXPORT_FORMATS = [
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('excel', 'Excel'),
    ]
    
    content_type = forms.ChoiceField(
        choices=[
            ('all', _('All Content')),
            ('articles', _('Articles')),
            ('courses', _('Courses')),
            ('books', _('Books')),
            ('scholarships', _('Scholarships')),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Content Type'),
        initial='all'
    )
    
    format = forms.ChoiceField(
        choices=EXPORT_FORMATS,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Export Format'),
        initial='csv'
    )
    
    include_images = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        label=_('Include Images'),
        help_text=_('Include featured images in export (will create a zip file)')
    )
    
    date_range = forms.ChoiceField(
        choices=[
            ('all', _('All Time')),
            ('today', _('Today')),
            ('week', _('This Week')),
            ('month', _('This Month')),
            ('year', _('This Year')),
            ('custom', _('Custom Range')),
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Date Range'),
        initial='all'
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        }),
        label=_('Start Date')
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-input',
            'type': 'date'
        }),
        label=_('End Date')
    )
    
    def clean(self):
        cleaned_data = super().clean()
        date_range = cleaned_data.get('date_range')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if date_range == 'custom':
            if not start_date or not end_date:
                raise forms.ValidationError(_('Please select both start and end dates for custom range.'))
            if start_date > end_date:
                raise forms.ValidationError(_('Start date must be before end date.'))
        
        return cleaned_data


class BackupSettingsForm(forms.Form):
    """Form for backup settings"""
    AUTO_BACKUP_CHOICES = [
        ('disabled', _('Disabled')),
        ('daily', _('Daily')),
        ('weekly', _('Weekly')),
        ('monthly', _('Monthly')),
    ]
    
    auto_backup = forms.ChoiceField(
        choices=AUTO_BACKUP_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label=_('Automatic Backups'),
        initial='disabled'
    )
    
    backup_database = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        label=_('Include Database'),
        help_text=_('Include database in backups')
    )
    
    backup_media = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        label=_('Include Media Files'),
        help_text=_('Include uploaded media files in backups')
    )
    
    keep_backups = forms.IntegerField(
        min_value=1,
        max_value=100,
        initial=30,
        widget=forms.NumberInput(attrs={'class': 'form-input'}),
        label=_('Keep Last N Backups'),
        help_text=_('Number of backups to keep (older backups will be deleted)')
    )
    
    backup_location = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': '/path/to/backup/folder or remote URL'
        }),
        label=_('Backup Location'),
        help_text=_('Local folder path or remote storage URL (leave empty for default location)')
    )
    
    encryption_key = forms.CharField(
        max_length=256,
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Encryption key (optional)'
        }),
        label=_('Encryption Key'),
        help_text=_('Optional encryption key for securing backup files')
    )


class CacheSettingsForm(forms.Form):
    """Form for cache settings"""
    cache_enabled = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        label=_('Enable Caching'),
        help_text=_('Improve site performance by caching frequently accessed data')
    )
    
    cache_timeout = forms.IntegerField(
        min_value=60,
        max_value=86400,
        initial=3600,
        widget=forms.NumberInput(attrs={'class': 'form-input'}),
        label=_('Cache Timeout (seconds)'),
        help_text=_('How long to keep cached data (1 hour = 3600 seconds)')
    )
    
    clear_cache_on_save = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        label=_('Clear Cache on Save'),
        help_text=_('Automatically clear cache when content is updated')
    )
    
    cache_pages = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        label=_('Cache Pages'),
        help_text=_('Cache entire page responses for anonymous users')
    )
    
    cache_queries = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'form-checkbox'}),
        label=_('Cache Database Queries'),
        help_text=_('Cache frequently used database queries')
    )
    
    def clean_cache_timeout(self):
        timeout = self.cleaned_data.get('cache_timeout')
        if timeout < 60:
            raise forms.ValidationError(_('Cache timeout must be at least 60 seconds.'))
        return timeout


# Widget for rich text editor
class RichTextEditorWidget(forms.Textarea):
    """Custom widget for rich text editor"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'rich-text-editor',
            'rows': 10,
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        output = super().render(name, value, attrs, renderer)
        # Add CKEditor initialization
        output += f'''
        <script>
            if (typeof CKEDITOR !== 'undefined') {{
                CKEDITOR.replace('id_{name}');
            }}
        </script>
        '''
        return output
