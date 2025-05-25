from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'w-full p-2 rounded-lg border dark:bg-darkHover dark:text-white',
            'rows': '4',
            'placeholder': 'Write your comment here...'
        })
    )

    class Meta:
        model = Comment
        fields = ['content']