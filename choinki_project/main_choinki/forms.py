from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from . import models
from django.forms import ModelForm, formset_factory


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=255)
    email = forms.EmailField(required=True)
    message = forms.CharField(widget=forms.Textarea)


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=False)      
    
    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]


class CustomerForm(ModelForm):
    phone_number = forms.DecimalField(required=False)   
    home = forms.CharField(required=False)   

    class Meta:
        model = models.Customer
        fields = ['first_name', 'last_name', 'phone_number', 'home']


class TreeForm(ModelForm):
    class Meta:
        model = models.Tree
        fields = ['type', 'localization', 'price']


class TreeFormsQuantity(forms.Form):
    quantity = forms.IntegerField(min_value=1, max_value=50)


class OrderForm(ModelForm):
    class Meta:
        model = models.Order
        fields = ['status']