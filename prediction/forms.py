from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import Diamond

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data


class LoginForm(AuthenticationForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class DiamondForm(forms.ModelForm):
    class Meta:
        model = Diamond
        fields = '__all__'
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input bg-gray-800 text-white rounded p-2 w-full'}),   
            'carat': forms.NumberInput(attrs={'class': 'form-input bg-gray-800 text-white rounded p-2 w-full', 'step': '0.01'}),
            'cut': forms.Select(attrs={'class': 'w-full p-3 bg-gray-800 text-white border-2 border-gray-600 rounded-md'}),
            'clarity': forms.Select(attrs={'class': 'w-full p-3 bg-gray-800 text-white border-2 border-gray-600 rounded-md'}),
            'color': forms.Select(attrs={'class': 'w-full p-3 bg-gray-800 text-white border-2 border-gray-600 rounded-md'}),
            'depth': forms.NumberInput(attrs={'class': 'form-input bg-gray-800 text-white rounded p-2 w-full', 'step': '0.01'}),
            'table': forms.NumberInput(attrs={'class': 'form-input bg-gray-800 text-white rounded p-2 w-full', 'step': '0.01'}),
            'x': forms.NumberInput(attrs={'class': 'form-input bg-gray-800 text-white rounded p-2 w-full', 'step': '0.01'}),
            'y': forms.NumberInput(attrs={'class': 'form-input bg-gray-800 text-white rounded p-2 w-full', 'step': '0.01'}),
            'z': forms.NumberInput(attrs={'class': 'form-input bg-gray-800 text-white rounded p-2 w-full', 'step': '0.01'}),
            'price_idr': forms.NumberInput(attrs={'class': 'form-input bg-gray-800 text-white rounded p-2 w-full'}),
        }