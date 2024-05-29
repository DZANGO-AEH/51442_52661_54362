from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from .models import CustomUser, UserProfile
from django.core.exceptions import ValidationError

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

class CustomUserUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        user = self.instance
        if user.stripe_account_id:
            self.fields['stripe_account_id'] = forms.CharField(
                label="Stripe Account ID",
                initial=user.stripe_account_id,
                widget=forms.TextInput(attrs={'readonly': 'readonly'})
            )

    def clean(self):
        cleaned_data = super().clean()
        user = self.instance
        if user.is_content_creator and not user.stripe_account_id:
            cleaned_data["stripe_account_id"] = None  # ensure it is not required if it doesn't exist
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
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

class PurchasePointsForm(forms.Form):
    points = forms.ChoiceField(choices=[(x, f'{x} points') for x in [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]], label='Number of points')

class WithdrawPointsForm(forms.Form):
    points = forms.IntegerField(min_value=1, label='Number of points')
