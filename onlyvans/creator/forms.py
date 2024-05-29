from django import forms
from .models import Post, Tier
from django.core.exceptions import ValidationError
from django.forms import ClearableFileInput
from django.utils.translation import gettext_lazy as _


from django import forms
from .models import Post, Tier

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'is_free', 'tier']
        labels = {
            'title': 'Title',
            'text': 'Content',
            'is_free': 'Is this a free post?',
            'tier': 'Choose a tier',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['tier'].queryset = Tier.objects.filter(user=user)
        # Update the 'tier' field required status based on the current input data or instance
        if self.data:
            is_free = self.data.get('is_free', 'off') == 'on'
        else:
            is_free = self.instance.is_free
        self.fields['tier'].required = not is_free

    def clean(self):
        cleaned_data = super().clean()
        is_free = cleaned_data.get('is_free')
        tier = cleaned_data.get('tier')

        if is_free:
            cleaned_data['tier'] = None
        elif not tier:
            self.add_error('tier', 'This field is required for paid posts.')

        return cleaned_data

class MediaForm(forms.Form):
    files = forms.FileField(label='Upload media files', required=False, widget=ClearableFileInput(attrs={'allow_multiple_selected': True}))

class TierForm(forms.ModelForm):
    class Meta:
        model = Tier
        fields = ['name', 'points_price', 'description', 'message_permission']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name']
        user = self.user
        if user and Tier.objects.filter(user=user, name=name).exists():
            raise forms.ValidationError("You already have a tier with this name.")
        return name

    def clean_points_price(self):
        price = self.cleaned_data.get('points_price')
        if price is not None and price <= 0:
            raise ValidationError(_("Price must be greater than zero."))
        return price

    def clean(self):
        cleaned_data = super().clean()
        if self.user and Tier.objects.filter(user=self.user).count() >= 12:
            raise forms.ValidationError("You cannot have more than 12 tiers.")
        return cleaned_data