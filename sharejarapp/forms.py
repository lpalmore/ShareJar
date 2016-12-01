from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django import forms
from django.forms import ModelForm
from models import Member, Charity, Balances, Invite, Team
from django.core.exceptions import ValidationError

class UserForm(ModelForm):

    paypalEmail = forms.EmailField(label='Paypal Email')

    class Meta:
        model = User
        fields = ('username','email', 'password')
    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("That Username is already taken")
        return username

#FIXLATER: create add balance increment form
class AddBalanceForm(forms.Form):
    increment = forms.DecimalField(max_digits=5, decimal_places=2, label="Amount")
    charity = forms.ModelChoiceField(queryset=Charity.objects.all(), to_field_name="charityname")


class MakePaymentForm(forms.Form):
    amount = forms.IntegerField(max_value=100, min_value=1)

class EditCharityForm(forms.Form):
   charityname = forms.CharField(max_length=80, label='New Name', required=False)
   description = forms.CharField(max_length=150, label="New Description", required=False)
   paypal_email = forms.EmailField(label="New Paypal Email", required=False)

   class Meta:
        model = Charity
        fields = ('charityname', 'description', 'paypal_email')

   def clean_charityname(self):
        charityname = self.cleaned_data['charityname']
        if Charity.objects.filter(charityname=charityname).exists():
            raise forms.ValidationError("A charity with that name already exists.")
        return charityname

   def clean_paypal_email(self):
        paypal_email = self.cleaned_data['paypal_email']
        if Charity.objects.filter(paypal_email=paypal_email).exists():
            raise forms.ValidationError("A charity with that email already exists.")
        return paypal_email

class LookupCharityForm(forms.Form):
    charityname = forms.CharField(max_length=80, label='Charity Name', widget=forms.TextInput(attrs={'class': 'form-control'}))

class LookupUserForm(forms.Form):
    username = forms.CharField(max_length=80, label='Username', widget=forms.TextInput(attrs={'class': 'form-control'}))

class CharityForm(ModelForm):

    class Meta:
        model = Charity
        fields = ('charityname', 'description', 'paypal_email')
    def clean_charityname(self):
        charityname = self.cleaned_data['charityname']
        if Charity.objects.filter(charityname=charityname).exists():
            raise forms.ValidationError("A charity with that name already exists.")
        return charityname
    def clean_paypal_email(self):
        paypal_email = self.cleaned_data['paypal_email']
        if Charity.objects.filter(paypal_email=paypal_email).exists():
            raise forms.ValidationError("A charity with that email already exists.")
        return paypal_email

class CreateTeamForm(forms.Form):
    name = forms.CharField(max_length=80, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Team Name'}))

class ChangeTeamNameForm(forms.Form):
    name = forms.CharField(max_length=80, widget=forms.TextInput(attrs={'class': 'form-control'}))

class InviteTeamForm(forms.Form):
    # How can I make this match the username field?
    username = forms.CharField(max_length=80)

class JoinTeamForm(forms.Form):
    team = None
    def __init__(self, *args, **kwargs):
        currentMember = kwargs.pop('member', None)
        super(JoinTeamForm, self).__init__(*args, **kwargs)
        if currentMember is not None:
            self.fields['team'] = forms.ModelChoiceField(queryset=Invite.objects.filter(member=currentMember))
