# forms.py
from django import forms
from .models import CycleDay, CycleSetting, Cycle
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    birth_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'birth_date', 'password1', 'password2']

class CycleSettingForm(forms.ModelForm):
    class Meta:
        model = CycleSetting
        exclude = ['user', 'last_updated']
        widgets = {
            'average_cycle_length': forms.NumberInput(attrs={'min': 20, 'max': 45}),
            'average_period_length': forms.NumberInput(attrs={'min': 2, 'max': 10}),
            'cycle_variation': forms.NumberInput(attrs={'min': 0, 'max': 7}),
        }

class CycleDayForm(forms.ModelForm):
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    
    class Meta:
        model = CycleDay
        exclude = ['user']
        widgets = {
            'temperature': forms.NumberInput(attrs={'step': '0.1'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['symptoms'].widget = forms.CheckboxSelectMultiple()

