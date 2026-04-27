from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('book/', views.book_slot, name='book_slot'),
    path('add-vehicle/', views.add_vehicle, name='add_vehicle'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('cancel/<int:booking_id>/', views.cancel_booking, name='cancel_booking'),
    
    # Authentication URLs
    path('login/', views.user_login, name='login'),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
    
    # Admin Portal URLs
    path('admin-portal/', views.admin_dashboard, name='admin_dashboard'),
    path('admin-portal/slots/', views.manage_slots, name='manage_slots'),
    path('admin-portal/slots/add/', views.add_slot, name='add_slot'),
    path('admin-portal/slots/delete/<int:slot_id>/', views.delete_slot, name='delete_slot'),
    path('admin-portal/bookings/', views.all_bookings, name='all_bookings'),
    path('admin-portal/bookings/cancel/<int:booking_id>/', views.admin_cancel_booking, name='admin_cancel_booking'),
]
