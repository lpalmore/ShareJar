from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm
from models import Member, Charity, Balances

class UserForm(ModelForm):

    paypalEmail = forms.EmailField(label='Paypal Email')

    class Meta:
        model = User
        fields = ('username','email', 'password')

#FIXLATER: create add balance increment form
class AddBalanceForm(forms.Form):
    increment = forms.DecimalField(max_digits=5, decimal_places=2, label="Amount")
    charity = forms.ModelChoiceField(queryset=Charity.objects.all(), to_field_name="charityname")


class MakePaymentForm(forms.Form):
    amount = forms.IntegerField(max_value=100, min_value=1)

class AddCharityForm(forms.Form):
   charityname = forms.CharField(max_length=80, label='Charity Name')
   description = forms.CharField(max_length=150, label="Description")
   paypal_email = forms.EmailField(label="Charity Email")