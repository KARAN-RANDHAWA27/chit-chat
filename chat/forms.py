from django import forms
from django.contrib.auth import get_user_model
from .models import Chat

User = get_user_model()

class GroupChatForm(forms.ModelForm):
    participants = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'select2'}),
        required=True
    )

    class Meta:
        model = Chat
        fields = ['name', 'participants']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-input', 'placeholder': 'Group Name'})
        self.fields['participants'].widget.attrs.update({'class': 'form-select'})

    def clean_participants(self):
        participants = self.cleaned_data['participants']
        if participants.count() < 2:
            raise forms.ValidationError("A group chat must have at least 2 participants.")
        return participants