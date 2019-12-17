from django import forms
from django.contrib.auth.models import User
from .models import Post,Forum,thread,Comment,Contact

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('title','body')

class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('body',)

class ThreadForm(forms.ModelForm):

    class Meta:
        model = thread
        fields = ('title','description')

class ForumForm(forms.ModelForm):

    class Meta:
        model  = Forum
        fields = ('title','description')

class ContactForm(forms.ModelForm):

    class Meta:
        model = Contact
        fields = '__all__'
