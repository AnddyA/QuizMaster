from django import forms
from .models import *

class StudentRegisterForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['dni', 'first_name', 'last_name']
        widgets = {
            'dni': forms.TextInput(attrs={'placeholder': 'Cédula'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Nombre'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Apellido'}),
        }

class StudentLoginForm(forms.Form):
    dni = forms.CharField(max_length=10, widget=forms.TextInput(attrs={'placeholder': 'Cédula'}))


class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['id','name']
        widgets = {
            'id': forms.TextInput(attrs={'placeholder': 'ID del grupo (5 caracteres)'}),
            'name': forms.TextInput(attrs={'placeholder': 'Nombre único del grupo'})
        }

class JoinGroupForm(forms.Form):

    group_id = forms.CharField(max_length=5, widget=forms.TextInput(attrs={'placeholder': 'ID del grupo'}))    

class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ['statement', 'image', 'category']

class OptionForm(forms.ModelForm):
    class Meta:
        model = Option
        fields = ['text', 'is_correct']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'profile_pic']