from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.conf import settings

# Creating the user model here.
class Profile(models.Model):
    """Model representing the user"""
    user= models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    date_of_birth = models.DateField(null = True, blank=True)
    phone_number = models.CharField(max_length=200)
    USER_TYPE_CHOICES = (
        ('S', 'student'),
        ('L', 'landlord'),
    )
    user_type = models.CharField(max_length=1, choices=USER_TYPE_CHOICES)
    
    def __str__(self):
        """String for representing the model object"""
        return f'{self.user.username} {self.user.last_name} '
    def get_absolute_url(self):
        """Returns the urls access a detail record for the user"""
        return reverse('profile-detail', args=[str(self.id)])
    
class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    accommodation = models.ForeignKey('Accommodation', on_delete=models.SET_NULL, null=True)
    booking_date = models.DateField()
    is_confirmed = models.BooleanField(default=False)
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateField(null=True, blank=True)

    def __str__(self):
        """string for representing the model"""
        return f'{self.user.username} {self.house} {self.booking_date}'
class Accommodation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, unique=False)
    name = models.CharField(max_length=100)
    description = models.TextField()
    address = models.CharField(max_length=100, null=True, blank=True)
    #price information
    cost_per_month = models.DecimalField(max_digits=10, decimal_places=2)
    deposit = models.DecimalField(max_digits=10, decimal_places=2)
    #Availability of the house
    available_from = models.DateField()
    available_to = models.DateField()
    #Images of the house
    image = models.ImageField(upload_to = 'house_image')
    image_2 = models.ImageField(upload_to = 'house_image', null=True, blank=True)
    image_3 = models.ImageField(upload_to = 'house_image', null=True, blank=True)
    #Checked for booking
    is_booked = models.BooleanField(default=False)
    def get_absolute_url(self):
        """Returns the urls access a detail record for the house"""
        return reverse('accommodation-detail', args=[str(self.id)])

    def __str__(self):
        """string for representing the model"""
        return f'{self.name}'
    
class Enquiry(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    accommodation = models.ForeignKey('Accommodation', on_delete=models.SET_NULL, null=True)
    enquiry_date = models.DateTimeField(auto_now_add=True)

    def get_absolute_url(self):
        """Returns the urls access a detail record for the user"""
        return reverse('enquiry-detail', args=[str(self.id)])
    
    def __str__(self):
        """string for representing the model"""
        return f'{self.user.username} {self.accommodation.name} '


class Message(models.Model):
    send = models.ForeignKey(User, on_delete=models.CASCADE, related_name='send')
    receive = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receive')
    title = models.CharField(max_length=50)
    body = models.TextField()
    date = models.DateTimeField(auto_now_add=True)