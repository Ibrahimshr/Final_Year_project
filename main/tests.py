from django.test import TestCase
from django.contrib.auth.models import User
from .models import Profile, Accommodation, Booking, Enquiry
import datetime

class ProfileModelTest(TestCase):
    def setUp(self):
    # Create a new user for each test
        self.username = 'testuser'
        self.password = 'testpass'
        self.user = User.objects.create_user(
        username=self.username,
        password=self.password
    )
class ProfileIntegrationTestCase(TestCase):
    def setUp(self):
        # Create a new user for each test
        self.username = 'testuser'
        self.password = 'testpass'
        self.user = User.objects.create_user(
            username=self.username,
            password=self.password
        )
    def test_create_profile(self):
        # Create a new profile instance
        profile, created = Profile.objects.get_or_create(user=self.user)
        # Check that the profile instance was created and saved to the database
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(Profile.objects.first(), profile)
    def test_update_profile(self):
        # Create a new profile instance
        profile, created = Profile.objects.get_or_create(user=self.user)
        # Update the profile instance
        profile.date_of_birth = '2001-07-02'
        profile.save()
        # Check that the profile instance was updated in the database
        self.assertEqual(Profile.objects.count(), 1)
        self.assertEqual(Profile.objects.first().date_of_birth, datetime.date(2001, 7, 2))
class AccommodationModelTestCase(TestCase):
     def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        # Create an accommodation
        self.accommodation = Accommodation.objects.create(            
            name='pack horse',
            description='studio House',
            address='sss',
            cost_per_month=2000,
            deposit=500,
            available_from='2023-05-11',
            available_to='2023-07-07',
            image='test_image.jpg',
            is_booked=False,
            user=self.user
        )
     def test_create_accommodation(self):
         #check that the accommodation was created in the database
         self.assertEqual(Accommodation.objects.count(), 1)
         self.assertEqual(Accommodation.objects.first().name, 'pack horse')
     def test_string_representation(self):
         #Test the string representation of the accommodation
         expected_str = self.accommodation.name
         self.assertEqual(str(self.accommodation), expected_str)
class BookingModelTestCase(TestCase):
     def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        # Create a booking
        self.booking = Booking.objects.create(            
            booking_date='2022-07-01',
            is_confirmed=False,
            payment_amount=500,
            user=self.user
        )
     def test_create_booking(self):
         #check that the booking was created in the database
         self.assertEqual(Booking.objects.count(), 1)
         self.assertEqual(Booking.objects.first().booking_date, datetime.date(2022,7,1))
class EnquiryModelTestCase(TestCase):
     def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass'
        )
        # Create a enquiry
        self.enquiry = Enquiry.objects.create(            
            message='enquiry about the pack horse',
            user=self.user
        )
     def test_create_enquiry(self):
         #check that the enquiry was created in the database
         self.assertEqual(Enquiry.objects.count(), 1)
         self.assertEqual(Enquiry.objects.first().message, 'enquiry about the pack horse')
     

