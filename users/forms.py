from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    first_name = forms.CharField(widget=forms.TextInput(attrs={'required':'True'}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={'required':'True'}))

    class Meta:
        model = User
        fields = ['first_name','last_name','username', 'email', 'password1', 'password2']

    def clean_email(self):
	    data = self.cleaned_data['email']
	    if User.objects.filter(email=data).exists():
	        raise forms.ValidationError("This email already used")
	    return data   
    

class UserUpdateForm(forms.ModelForm):
	first_name = forms.CharField(widget=forms.TextInput(attrs={'required':'True'}))
	last_name = forms.CharField(widget=forms.TextInput(attrs={'required':'True'}))

	class Meta:
		model = User
		fields = ['first_name','last_name','email']


class ProfileUpdateForm(forms.ModelForm):
	class Meta:
		model = Profile
		fields = ['image']

        