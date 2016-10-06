from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm

class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        
#FIXLATER: create add balance increment form
class AddBalanceForm(forms.Form):
	increment = forms.DecimalField(max_digits=5, decimal_places=2)