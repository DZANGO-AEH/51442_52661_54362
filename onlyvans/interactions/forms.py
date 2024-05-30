from django import forms
from .models import Message


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'placeholder': 'Type your message here...', 'rows': 3}),
        }
        labels = {
            'body': '',
        }