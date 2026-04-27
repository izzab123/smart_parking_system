from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.
class Vehicle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle_number = models.CharField(max_length=20)
    vehicle_type = models.CharField(max_length=10)

    def __str__(self):
        return self.vehicle_number

class ParkingSlot(models.Model):
    slot_number = models.CharField(max_length=10)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.slot_number

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    slot = models.ForeignKey(ParkingSlot, on_delete=models.CASCADE)
    booking_time = models.DateTimeField(default=timezone.now)
    expiry_time = models.DateTimeField()
    status = models.CharField(max_length=20, default='Active')

    def __str__(self):
        return f"{self.user.username} - {self.slot.slot_number}"