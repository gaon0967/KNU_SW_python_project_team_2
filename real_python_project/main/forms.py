# main/forms.py
from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = [
            'category',  # 자유/신고
            'name',
            'gender',
            'age',
            'region',
            'email',
            'title',
            'content',
        ]
        widgets = {
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 rounded border'}),
            'name':     forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded border'}),
            'gender':   forms.Select(attrs={'class': 'w-full px-4 py-2 rounded border'}),
            'age':      forms.NumberInput(attrs={'class': 'w-full px-4 py-2 rounded border'}),
            'region':   forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded border', 'placeholder':'예: 강남구'}),
            'email':    forms.EmailInput(attrs={'class': 'w-full px-4 py-2 rounded border'}),
            'title':    forms.TextInput(attrs={'class': 'w-full px-4 py-2 rounded border'}),
            'content':  forms.Textarea(attrs={'class': 'w-full px-4 py-2 rounded border', 'rows':6}),
        }
