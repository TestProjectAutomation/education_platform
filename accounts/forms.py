from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # تحسين رسائل المساعدة
        self.fields['username'].help_text = _(
            'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        )
        self.fields['password1'].help_text = _(
            'Your password must contain at least 8 characters.'
        )

class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'profile_picture',
            'bio', 'phone', 'facebook_url', 'twitter_url', 'linkedin_url'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

class AdminUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name',
            'user_type', 'is_active', 'is_staff', 'is_superuser'
        ]