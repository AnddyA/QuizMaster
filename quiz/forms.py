from django import forms
from .models import Student, Group

class StudentRegisterForm(forms.ModelForm):
    class Meta:
        model = Student
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
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Nombre único del grupo'})
        }

class JoinGroupForm(forms.Form):
    group_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Nombre del grupo'}))
