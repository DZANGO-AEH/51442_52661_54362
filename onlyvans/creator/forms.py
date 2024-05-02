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


class MediaForm(forms.Form):
    class MediaForm(forms.Form):
        files = forms.FileField(label='Upload media files', required=False)


class TierForm(forms.ModelForm):
    class Meta:
        model = Tier
        fields = ['name', 'price', 'description', 'message_permission']