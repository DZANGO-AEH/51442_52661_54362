from django import forms
from .models import Post, Tier
from django.core.exceptions import ValidationError
from django.forms import ClearableFileInput


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
        super().__init__(*args, **kwargs)
        self.fields['tier'].required = False

    def clean(self):
        cleaned_data = super().clean()
        is_free = cleaned_data.get('is_free')
        tier = cleaned_data.get('tier')

        # If the post is not free, ensure a tier is selected
        if not is_free and not tier:
            self.add_error('tier', 'This field is required for paid posts.')

        return cleaned_data


class MediaForm(forms.Form):
    files = forms.FileField(label='Upload media files', required=False, widget=ClearableFileInput(attrs={'allow_multiple_selected': True}))

class TierForm(forms.ModelForm):
    class Meta:
        model = Tier
        fields = ['name', 'price', 'description', 'message_permission']