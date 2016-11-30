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

class AddTeamBalanceForm(forms.Form):
    increment = forms.DecimalField(max_digits=5, decimal_places=2, label="Amount")
    team = None
    def __init__(self, *args, **kwargs):
        currentMember = kwargs.pop('member', None)
        super(AddTeamBalanceForm, self).__init__(*args, **kwargs)
        if currentMember is not None:
            self.fields['team'] = TeamModelChoiceField(queryset=currentMember.teammemberlist_set.all())


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
    charityname = forms.CharField(max_length=80, label='Charity Name')

class LookupUserForm(forms.Form):
    username = forms.CharField(max_length=80, label='Username')

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
    name = forms.CharField(max_length=80)
    def clean_name(self):
        name = self.cleaned_data['name']
        if Team.objects.filter(name=name).exists():
            raise forms.ValidationError("That name is already taken- please choose another.")
        return name

class InviteTeamForm(forms.Form):
    # How can I make this match the username field?
    username = forms.CharField(max_length=80)
    def clean_username(self):
        username = self.cleaned_data['username']
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError("No user with that username exists.")
        return username

class JoinTeamForm(forms.Form):
    team = None
    def __init__(self, *args, **kwargs):
        currentMember = kwargs.pop('member', None)
        super(JoinTeamForm, self).__init__(*args, **kwargs)
        if currentMember is not None:
            self.fields['team'] = forms.ModelChoiceField(queryset=Invite.objects.filter(member=currentMember))

class LeaveTeamForm(forms.Form):
    team = None
    def __init__(self, *args, **kwargs):
        currentMember = kwargs.pop('member', None)
        super(LeaveTeamForm, self).__init__(*args, **kwargs)
        if currentMember is not None:
            self.fields['team'] = TeamModelChoiceField(queryset=currentMember.teammemberlist_set.all())

class TeamModelChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.team.name
