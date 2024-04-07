from . models import Post, Like, Comment, Favourite, Media, Tier
from django.forms import ModelForm

class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'text', 'is_free', 'tier', 'content']
        labels = {
            'title': 'Title',
            'text': 'Content',
            'is_free': 'Is this a free post?',
            'tier': 'Choose a tier',
            'content': 'Content'
        }