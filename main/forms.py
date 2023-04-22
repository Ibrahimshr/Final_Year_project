from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Booking, Accommodation, Enquiry

class UserRegisterForm(UserCreationForm):
    first_name= forms.CharField()
    last_name= forms.CharField()
    email = forms.EmailField()
    

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class UserUpdateForm(forms.ModelForm):
    first_name= forms.CharField()
    last_name= forms.CharField()
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name' ]

class ProfileUpdateForm(forms.ModelForm):
    USER_TYPE_CHOICES = (
        ('S', 'student'),
        ('L', 'landlord'),
    )
    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES)

    class Meta:
        model = Profile
        fields = ['date_of_birth',  'phone_number', 'user_type' ]

class AccommodationForm(forms.ModelForm):
    class Meta:
        model = Accommodation
        exclude = ["user"]
        fields = ['name', 'description', 'address', 'cost_per_month', 'deposit', 'available_from', 'available_to', 'image']
        widgets = {
            'available_from': forms.DateInput(attrs ={'type': 'date'}),
            'available_to': forms.DateInput(attrs={'type': 'date'}),
        }

class EnquiryForm(forms.ModelForm):
    class Meta:
        model = Enquiry
        fields = ['message']
        widgets = {
            'enquiry_date': forms.DateInput(attrs ={'type': 'date'}),
        }

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['accommodation', 'booking_date', 'payment_amount']
        widgets = {
            'booking_date': forms.DateInput(attrs ={'type': 'date'}),
        }
class UserSearchForm(forms.Form):
    username = forms.CharField(max_length=100)