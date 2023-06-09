from django.shortcuts import render
import requests
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from .models import Accommodation, Booking, Enquiry, Message
from .forms import EnquiryForm
from django.http import Http404
from django.http import HttpResponseRedirect
from project import settings
from decimal import Decimal
from django.core.mail import send_mail, EmailMessage
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm, AccommodationForm, EnquiryForm, BookingForm, MessageForm
from datetime import datetime
from django.views.generic.edit import DeleteView
from django.template import loader
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from . tokens import generate_token
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
# AdminView class dependencies
from .forms import UserSearchForm
from django.contrib import admin
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import formset_factory

# Create your views here.
def main(request):
    """View Function for home page of this site"""
    #Getting the properties using the api
    api_key = ' '
    url = f'https://api.zoopla.co.uk/api/v1/property_listings.js?area=greater+manchester&api_key={api_key}'
    response = requests.get(url)
    try:
        listings = response.json()['listing']
    except ValueError as e:
        # handle the error here, e.g. by logging it or showing an error message to the user
        print(f"Error decoding JSON response: {e}")
        listings = []
    context = {'listings': listings}
    #render the html template main.html
    return render(request, 'main.html', context)
    
   
# Function to check if the user is a client
def is_client(user):
    if user.is_staff or user.is_superuser:
        return False
    else:
        return True

# Create a new view for the admin page
class AdminView(LoginRequiredMixin, TemplateView):
    # Set the template for the view
    template_name = 'main/admin.html'

    def dispatch(self, request, *args, **kwargs):
    # Check if the user is a staff or admin
        if not request.user.is_staff and not request.user.is_superuser:
        # If not, redirect to the home page
            return redirect('main')

    # If the user is a staff or admin, proceed with handling the request
        return super().dispatch(request, *args, **kwargs)

    # Add a form for searching for users by username
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = UserSearchForm()
        return context

    # Handle POST requests
    def post(self, request, *args, **kwargs):

        # Check if the user is a staff or admin
        if not request.user.is_staff and not request.user.is_superuser:
        # If not, redirect to the home page
            return 
            redirect('main')

        form = UserSearchForm(request.POST)
        if form.is_valid():
            # Perform the search and return the results
            users = User.objects.filter(username=form.cleaned_data['username'])
            return render(request, self.template_name, {'users': users})
        else:
            return render(request, self.template_name, {'form': form})




# Admin view for updating users
@login_required
def update_user_profile(request, username):
    user = User.objects.get(username=username)
    # Check if the user is a staff or admin
    if not request.user.is_staff and not request.user.is_superuser:
        # If not, redirect to the home page
        return redirect('main')

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=user)
        p_form = ProfileUpdateForm(request.POST, 
        request.FILES, 
        instance=user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(
                request, f'User\'s account has been updated.')
            return redirect('admin')
    else:
        u_form = UserUpdateForm(instance=user)
        p_form = ProfileUpdateForm(instance=user.profile)
    
    context = {
       'u_form': u_form,
       'p_form': p_form, 
    }
    return render(request, 'main/update_user_profile.html', context)

# User Registration
def register(request):
    # Making sure the user cannot access registration page if logged in
    if request.user.is_authenticated is True:
        return render(request, 'main/profile.html')

    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        form_email = form['email'].value()
        existing_users = User.objects.filter(email=form_email)

        # Existing Email Check
        if existing_users.count():
            messages.warning(request, f'Email has been used already!')
            form = UserRegisterForm()
            return render(request, 'main/register.html', {'form': form})

        # Validate form input and remove user admin privileges
        if form.is_valid():
            user = form.save()
            # default to non-active
            user.is_active = False
            user.is_staff = False
            user.is_superuser = False
            user.save()

            # Email details
            uid = urlsafe_base64_encode(force_bytes(User.objects.last().pk))
            current_site = get_current_site(request)
            domain = current_site.domain
            name = User.objects.last().first_name

            # Site account creation message.
            messages.success(request, f'Your account has been created. Please confirm your email to finish your registration!')

            # Welcome Email Setup
            subject = 'Welcome to Housing Company'
            message = "Thanks for having us. Please confirm your email to finish your registration!"
            sender = settings.EMAIL_HOST_USER
            receiver = User.objects.last().email
            password = settings.EMAIL_HOST_PASSWORD

            # Welcome Email Dispatch
            send_mail(subject, message, sender, [receiver], fail_silently=False, auth_password=password)

            # Confirmation Email Setup
            email_subject = "Confirm your Email @ Housing Company"
            message2 = render_to_string('main/confirmation_email.html', {
                'name': user.first_name,
                'domain': domain,
                'uid': uid,
                'token': generate_token.make_token(user)
            })

            # Confirmation Email Setup
            email = EmailMessage(
                email_subject,
                message2,
                settings.EMAIL_HOST_USER,
                [receiver],
            )
            # Confirmation Email Dispatch
            email.fail_silently = True
            email.send()
            return redirect('two_factor:login')
        else:
            # Error message and registration form reset
            messages.warning(request, f'Error please try again!')
            form = UserRegisterForm()
            return render(request, 'main/register.html', {'form': form})
    else:
        form = UserRegisterForm()
        return render(request, 'main/register.html', {'form': form})


@login_required
@user_passes_test(is_client)
def profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, f'Your Account Has Been Updated')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form' : u_form,
        'p_form' : p_form
    }
    return render(request, 'main/profile.html', context)

def activate(request, uidb64, token):
    try:
        user_id = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=user_id)
        messages.success(
                request, f'Your account has been created. Please confirm your email to finish your registration!')
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        myuser = None
    
    if user is not None and generate_token.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "Your Account has been activated!!")
        return redirect('two_factor:login')
        
    else:
        return render(request, 'main/activation_failed.html')

   
def accommodation_detail(request, pk):
    accommodation = get_object_or_404(Accommodation, pk=pk)
    form = EnquiryForm()
    return render(request, 'main/accommodation_detail.html', {'accommodation': accommodation, 'form': form, 'name': 'Accommodation'})

def accommodation_list(request):
    #Making sure only landlords can see their own houses they uploaded 
    if request.user.profile.user_type == 'L':
        accommodations = Accommodation.objects.all()
        my_accommodations = []
        for accommodation in accommodations:
            if request.user.username == accommodation.user.username:
                my_accommodations.append(accommodation)
        return render(request, 'main/accommodation_list.html', {'accommodations': my_accommodations})
    else:
        #The students can see all the houses available
        accommodations = Accommodation.objects.all()
        return render(request, 'main/accommodation_list.html', {'accommodations': accommodations})


def upload_accommodation(request):
    AccommodationFormSet = formset_factory(AccommodationForm, extra=1)
    if request.method == 'POST':
        formset = AccommodationFormSet(request.POST, request.FILES)
        if formset.is_valid():
            # Landlords and admins can only upload houses
            for form in formset:
                if form.is_valid():
                    accommodation = form.save(commit=False)
                    accommodation.user = request.user
                    accommodation.save()
            messages.success(request, 'Your accommodations have been uploaded successfully.')
            return redirect('main')
    else:
        formset = AccommodationFormSet()
    return render(request, 'main/upload_accommodation.html', {'formset': formset})

def delete_accommodation(request, pk):
    accommodation = get_object_or_404(Accommodation, pk=pk)
    if request.method == 'POST':
        #Admins can delete any houses but landlords can only delete their own houses
        accommodation.delete()
        messages.success(request, 'The accommodation has been deleted.')
        return redirect('main')
    return render(request, 'main/delete_accommodation.html', {'accommodation': accommodation})

def set_accommodation_booked(request, pk):
    accommodation = get_object_or_404(Accommodation, pk=pk)
    #Landlords can only marked their own house as booked
    if request.method == 'POST':
        accommodation.is_booked = True
        accommodation.save()
        messages.success(request, 'The accommodation has been set as booked.')
        return redirect('main')
    return render(request, 'main/set_accommodation_booked.html', {'accommodation': accommodation})

def set_accommodation_unbooked(request, pk):
    accommodation = get_object_or_404(Accommodation, pk=pk)
    #Landlords can only marked unbooked their own house
    if request.method == 'POST':
        accommodation.is_booked = False
        accommodation.save()
        messages.success(request, 'The accommodation has been set as unbooked.')
        return redirect('main')
    return render(request, 'main/set_accommodation_unbooked.html', {'accommodation': accommodation})

def guarantor_view(request):
    return render(request, 'main/guarantor.html')

def booking_or_enquiry(request, accommodation_id):
    accommodation = get_object_or_404(Accommodation, pk=accommodation_id)
    context = {'accommodation': accommodation}
    return render(request, 'main/booking_or_enquiry.html', context)


@login_required
def booking_create(request, accommodation_id):
    accommodation = get_object_or_404(Accommodation, pk=accommodation_id)
    if request.method == 'POST':
        booking_date = request.POST['booking_date']
        payment_amount = request.POST['payment_amount']
        booking = Booking(user=request.user, accommodation=accommodation, booking_date=booking_date, payment_amount=payment_amount)
        booking.save()
        accommodation.availability = False
        accommodation.save()

        #send email to the student
        if request.user.profile.user_type == 'S':
            subject = 'Your accommodation has been booked'
            message = 'Dear {},\n\nYour accommodation at {} has been successfully booked.\n\nThank you for using our application!\n\nBest regards,\nInter Accommodation Team'.format(request.user.first_name, accommodation.name)
            recipient_list = [request.user.email]
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list, fail_silently=False)

            # Send email to the landlord
            subject = 'Student Has Booked Your Accommodation'
            message = 'Dear {},\n\nA student has booked your accommodation at {}.\n\nPlease log in to your account to mark the accommodation as booked.\n\nThank you for using our application!\n\nBest regards,\nInter Accommodation Team'.format(accommodation.user.first_name, accommodation.name)
            recipient_list = [accommodation.user.email]
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list, fail_silently=False)

        messages.success(request, 'Booking confirmed! You will receive a confirmation email shortly.')
        return render(request, 'main/booking_success.html')
    else:
        form = BookingForm()
    return render(request, 'main/booking_create.html', {'form': form})

def booking_success(request):
    return render(request, 'main/booking_success.html')
    
def enquiry_create(request, accommodation_id):
    accommodation = get_object_or_404(Accommodation, pk=accommodation_id)
    if request.method == 'POST':
        form = EnquiryForm(request.POST)
        if form.is_valid():
            enquiry = form.save(commit=False)
            enquiry.user = request.user
            enquiry.accommodation = accommodation
            enquiry.save()

            # Send email to the landlord
            if request.user.profile.user_type == 'S':
                subject = 'New Enquiry from a student'
                message = 'Dear {},\n\nA student has made an enquiry about your accommodation at {}.\n\nMessage: {}\n\nYou can reply to the student directly using their email address: {}\n\nBest regards,\nInter Accommodation Team'.format(accommodation.user.first_name, accommodation.name, enquiry.message, request.user.email)
                recipient_list = [accommodation.user.email]
                send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list, fail_silently=False)
                messages.success(request, 'Enquiry sent! The accommodation owner will be in touch shortly.')
            else:
                messages.success(request, 'Enquiry sent!')
            return redirect('main')
    else:
        form = EnquiryForm()
    return render(request, 'main/enquiry_create.html', {'form': form})

@login_required
def send_message(request):   
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            receive_mail = request.POST.get('email')
            title = request.POST.get('title') 
            body = request.POST.get('body')
            message.send = User.objects.get(email=request.user.email)
            message.receive = User.objects.get(email=receive_mail)
            message.date = datetime.now()
            message.save()
            messages.success(request, 'Your message has been sent to the admin.')
            return redirect('main')
    else:
        form = MessageForm(request.POST)
        return render(request, 'main/send_message.html', {'form' : form})


@login_required 
def received_messages(request):   
    messages = Message.objects.order_by('-date')
    messages_received = []
    for x in messages:
        if x.receive != None:
            if x.receive.email == request.user.email:
                messages_received.append(x) 
    return render(request, 'main/received_messages.html', {'messages_received' : messages_received})


@login_required
def view_message(request, id):   
    message = Message.objects.get(id=id)
    return render(request, 'main/view_message.html', {'message' : message})


"""def search(request):
    query = request.GET.get('q')
    if query:
        accommodations = Accommodation.objects.filter(Q(location__icontains=query) | Q(name__icontains=query))
    else:
        accommodations = Accommodation.objects.filter(availability=True)
    return render(request, 'search_results.html', {'accommodations': accommodations, 'query': query})
"""