from django.contrib import admin
from .models import Profile, Booking, Accommodation, Enquiry, Message
# Register your models here.
admin.site.register(Profile)
admin.site.register(Message)
#admin.site.register(Booking)
#admin.site.register(Accommodation)
#admin.site.register(Enquiry)