from django import forms
from .models import Message

class MessageForm(forms.ModelForm):
    """
    Form for creating and sending messages.

    This form is linked to the Message model and includes a single field for the message body.
    The body field is rendered as a textarea with a placeholder and custom row size.
    """

    class Meta:
        model = Message
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={'placeholder': 'Type your message here...', 'rows': 3}),
        }
        labels = {
            'body': '',
        }
