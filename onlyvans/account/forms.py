from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from .models import CustomUser, UserProfile
from django.core.exceptions import ValidationError

RESERVED_USERNAMES = ['update', 'admin', 'administrator', 'login', 'logout', 'register', 'change-password',
                      'password-reset', 'password-reset-done', 'password-reset-confirm', 'password-reset-complete',
                      'dashboard', 'profile', 'settings', 'purchase-points', 'withdraw-points', 'stripe',
                      'messages', 'thread', 'like', 'favourite', 'subscribe', 'unsubscribe', 'post', 'posts',
                      'search', 'search-results', 'search-creators', 'search-posts', 'search-subscriptions',]


class CustomUserCreationForm(UserCreationForm):
    """
    Form for creating a new user. Inherits from Django's UserCreationForm.

    Meta:
        model: Specifies the model to use for this form (CustomUser).
        fields: The fields to include in the form.
    """

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2", "is_content_creator")

    def clean_username(self):
        """
        Validates that the username is not in the list of reserved usernames.

        Returns:
            str: The cleaned username.

        Raises:
            ValidationError: If the username is reserved.
        """
        username = self.cleaned_data['username'].lower()
        if username in RESERVED_USERNAMES:
            raise ValidationError("This username is reserved and cannot be used.")
        return username


class CustomUserChangeForm(UserChangeForm):
    """
    Form for updating a user. Inherits from Django's UserChangeForm.

    Meta:
        model: Specifies the model to use for this form (CustomUser).
        fields: The fields to include in the form.
    """

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'is_content_creator')


class CustomUserUpdateForm(forms.ModelForm):
    """
    Form for updating CustomUser details. This form allows updating the email,
    first name, and last name of the user. If the user has a Stripe account ID,
    the field is included but set to read-only and disabled.

    Meta:
        model: Specifies the model to use for this form (CustomUser).
        fields: Specifies the fields to include in the form.
    """

    class Meta:
        model = CustomUser
        fields = ('email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        """
        Initializes the form. If the user has a Stripe account ID, the field is added
        and set to read-only and disabled.

        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        super().__init__(*args, **kwargs)
        user = self.instance
        if user.stripe_account_id:
            self.fields['stripe_account_id'] = forms.CharField(
                label="Stripe Account ID",
                initial=user.stripe_account_id,
                widget=forms.TextInput(attrs={'readonly': 'readonly', 'disabled': 'disabled'}),
                required=False
            )

    def clean(self):
        """
        Cleans the form data. Ensures that stripe_account_id is not required if it doesn't exist
        for content creators.

        Returns:
            dict: The cleaned data.
        """
        cleaned_data = super().clean()
        user = self.instance
        if user.is_content_creator and not user.stripe_account_id:
            cleaned_data["stripe_account_id"] = None  # Ensure it is not required if it doesn't exist
        return cleaned_data


class UserProfileForm(forms.ModelForm):
    """
    Form for updating user profile details. Inherits from Django's ModelForm.

    Meta:
        model: Specifies the model to use for this form (UserProfile).
        fields: The fields to include in the form.
    """

    class Meta:
        model = UserProfile
        fields = ['profile_pic', 'background_pic', 'description', 'website_url', 'twitter_url', 'instagram_url']


class UserPasswordChangeForm(PasswordChangeForm):
    """
    Form for changing a user's password. Inherits from Django's PasswordChangeForm.

    Meta:
        model: Specifies the model to use for this form (CustomUser).
        fields: The fields to include in the form.
    """

    class Meta:
        model = CustomUser
        fields = ('old_password', 'new_password1', 'new_password2')

    def __init__(self, *args, **kwargs):
        """
        Initializes the form and customizes field labels.
        """
        super(UserPasswordChangeForm, self).__init__(*args, **kwargs)
        self.fields['old_password'].label = "Current Password"
        self.fields['new_password1'].label = "New Password"
        self.fields['new_password2'].label = "Confirm New Password"