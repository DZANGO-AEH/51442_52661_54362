from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser, UserProfile
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import PasswordChangeForm


RESERVED_USERNAMES = ['update', 'admin', 'login', 'logout', 'register', 'change-password']


class CustomUserCreationForm(UserCreationForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2", "is_content_creator")

    def clean_username(self):
        username = self.cleaned_data['username'].lower()
        if username in RESERVED_USERNAMES:
            raise ValidationError("This username is reserved and cannot be used.")
        return username

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'is_content_creator')

from django import forms
from .models import CustomUser

class CustomUserUpdateForm(forms.ModelForm):
    same_email = forms.BooleanField(required=False, label="Use main email address as PayPal email")
    paypal_email = forms.EmailField(
        required=False,
        label="PayPal Email",
        help_text="Please ensure this is a valid PayPal email address."
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'same_email', 'paypal_email', 'first_name', 'last_name')
        exclude = {'username', 'password', 'is_content_creator'}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.instance
        if not user.is_content_creator:
            self.fields['same_email'].widget = forms.HiddenInput()
            self.fields['paypal_email'].widget = forms.HiddenInput()
            self.fields['same_email'].required = False
            self.fields['paypal_email'].required = False

    def clean(self):
        cleaned_data = super().clean()
        same_email = cleaned_data.get("same_email")
        email = cleaned_data.get("email")
        paypal_email = cleaned_data.get("paypal_email")
        user = self.instance

        if user.is_content_creator:
            if same_email and email:
                cleaned_data["paypal_email"] = email
            elif not same_email and not paypal_email:
                self.add_error("paypal_email", "Please provide a PayPal email address or select 'Use main email address as PayPal email'.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        if user.is_content_creator:
            if self.cleaned_data.get("same_email"):
                user.paypal_email = self.cleaned_data["email"]
            else:
                user.paypal_email = self.cleaned_data["paypal_email"]

        if commit:
            user.save()
        return user


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['profile_pic', 'background_pic', 'description', 'website_url', 'twitter_url', 'instagram_url']


class UserPasswordChangeForm(PasswordChangeForm):
    class Meta:
        model = CustomUser
        fields = ('old_password', 'new_password1', 'new_password2')

    def __init__(self, *args, **kwargs):
        super(UserPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].label = "Current Password"
        self.fields['new_password1'].label = "New Password"
        self.fields['new_password2'].label = "Confirm New Password"
