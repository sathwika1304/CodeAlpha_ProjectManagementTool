from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Project, Task, Comment


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ["name", "description", "members"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "members": forms.SelectMultiple(attrs={"size": 4}),
        }


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = [
            "title",
            "description",
            "assigned_to",
            "status",
            "priority",
            "due_date",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "due_date": forms.DateInput(attrs={"type": "date"}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={"rows": 2, "placeholder": "Write a comment..."}
            )
        }
