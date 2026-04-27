from django.contrib import admin
from .models import Vehicle, ParkingSlot, Booking

# Register your models here.
admin.site.register(Vehicle)
admin.site.register(ParkingSlot)
admin.site.register(Booking)