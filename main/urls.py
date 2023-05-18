from django.urls import path
from .import views

urlpatterns =[
    path('', views.main, name='main'),
    #Booking and enquiry urls
    path('accommodation/<int:pk>/', views.accommodation_detail, name='accommodation'), 
    
    path('accommodation/', views.accommodation_list, name='accommodation_list'),
    #path('accommodation/<int:pk>/delete/', views.delete_accommodation, name='delete_accommodation'),
    path('accommodation/<int:pk>/delete/', views.delete_accommodation, name='delete_accommodation'),
    path('accommodation/<int:pk>/booked/', views.set_accommodation_booked, name='set_accommodation_booked'),
    path('accommodation/<int:pk>/unbooked/', views.set_accommodation_unbooked, name='set_accommodation_unbooked'),
    path('accommodation/<int:accommodation_id>/booking_or_enquiry/', views.booking_or_enquiry, name='booking_or_enquiry'),
    path('booking/create/<int:accommodation_id>/', views.booking_create, name='booking_create'),
    path('enquiry/create/<int:accommodation_id>/', views.enquiry_create, name='enquiry_create'),
    path('accommodation/success/', views.booking_success, name='booking_success'),
    path('guarantor/', views.guarantor_view, name='guarantor'), 
    path('send_message/', views.send_message, name='send_message'), 
    path('received_messages/', views.received_messages, name='received_messages'), 
    path('view_message/<id>', views.view_message, name='view_message'), 
    
    


] 