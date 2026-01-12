from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Book, BookReview

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
            'title', 'slug', 'content', 'excerpt', 'featured_image',
            'categories', 'book_type', 'author', 'publisher',
            'publication_year', 'pages', 'isbn', 'download_link',
            'file', 'preview_pages', 'link_display_duration',
            'is_featured', 'status'
        ]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 10}),
            'excerpt': forms.Textarea(attrs={'rows': 3}),
        }

class BookReviewForm(forms.ModelForm):
    class Meta:
        model = BookReview
        fields = ['name', 'email', 'rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['rating'].widget = forms.HiddenInput()