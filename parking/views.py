from django.shortcuts import render, redirect
from .models import ParkingSlot, Booking, Vehicle
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Sum
from decimal import Decimal

def dashboard(request):
    slots = ParkingSlot.objects.all()
    available_count = slots.filter(is_available=True).count()
    occupied_count = slots.filter(is_available=False).count()
    
    # Get active bookings with vehicle images for occupied slots
    occupied_slots = []
    for slot in slots.filter(is_available=False):
        booking = Booking.objects.filter(slot=slot, status='Active').first()
        if booking:
            occupied_slots.append({
                'slot': slot,
                'booking': booking,
                'vehicle': booking.vehicle
            })
    
    # Fixed pricing: Bike=25 BDT, Car=50 BDT per hour
    for slot in slots:
        slot.bike_charge = Decimal('25.00')
        slot.car_charge = Decimal('50.00')
    
    return render(request, 'dashboard.html', {
        'slots': slots,
        'available_count': available_count,
        'occupied_count': occupied_count,
        'occupied_slots': occupied_slots
    })

@login_required(login_url='/login/')
def book_slot(request):
    if request.method == 'POST':
        vehicle_id = request.POST.get('vehicle')
        if not vehicle_id:
            messages.error(request, 'Please select a vehicle')
            return redirect('book_slot')
            
        vehicle = Vehicle.objects.get(id=vehicle_id)

        slot = ParkingSlot.objects.filter(is_available=True).first()
        if slot:
            slot.is_available = False
            slot.save()

            # Fixed pricing based on vehicle type for 1 hour
            if vehicle.vehicle_type.lower() == 'bike':
                total_price = Decimal('25.00')
            else:  # car or other
                total_price = Decimal('50.00')

            booking = Booking.objects.create(
                user=request.user,
                vehicle=vehicle,
                slot=slot,
                expiry_time=timezone.now() + timedelta(hours=1),
                total_price=total_price
            )
            messages.success(request, f'Slot {slot.slot_number} booked successfully! Price: BDT {total_price} (1 hour)')
            return redirect('my_bookings')
        else:
            messages.error(request, 'No available slots at the moment')

    vehicles = Vehicle.objects.filter(user=request.user)
    slots = ParkingSlot.objects.filter(is_available=True)
    
    # Fixed pricing: Bike=25 BDT, Car=50 BDT per hour
    for slot in slots:
        slot.bike_charge = Decimal('25.00')
        slot.car_charge = Decimal('50.00')
    
    return render(request, 'book.html', {'vehicles': vehicles, 'slots': slots})

@login_required(login_url='/login/')
def add_vehicle(request):
    if request.method == 'POST':
        vehicle_number = request.POST.get('vehicle_number')
        vehicle_type = request.POST.get('vehicle_type')
        vehicle_image = request.FILES.get('vehicle_image')
        
        Vehicle.objects.create(
            user=request.user,
            vehicle_number=vehicle_number,
            vehicle_type=vehicle_type,
            vehicle_image=vehicle_image
        )
        messages.success(request, 'Vehicle added successfully!')
    return redirect('book_slot')

@login_required(login_url='/login/')
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_time')
    return render(request, 'My_bookings.html', {'bookings': bookings})

@login_required(login_url='/login/')
def cancel_booking(request, booking_id):
    if request.method == 'POST':
        booking = Booking.objects.get(id=booking_id, user=request.user)
        booking.status = 'Cancelled'
        booking.slot.is_available = True
        booking.slot.save()
        booking.save()
        messages.success(request, 'Booking cancelled successfully!')
        return redirect('submit_review', booking_id=booking_id)
    return redirect('my_bookings')

def user_login(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password')
    
    return render(request, 'login.html')

def user_register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        if password1 != password2:
            messages.error(request, 'Passwords do not match')
            return render(request, 'register.html')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return render(request, 'register.html')
        
        user = User.objects.create_user(username=username, password=password1)
        login(request, user)
        messages.success(request, 'Registration successful! Welcome!')
        return redirect('dashboard')
    
    return render(request, 'register.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'Logged out successfully!')
    return redirect('dashboard')


# Admin Portal Views
@staff_member_required
def admin_dashboard(request):
    total_slots = ParkingSlot.objects.count()
    available_slots = ParkingSlot.objects.filter(is_available=True).count()
    occupied_slots = ParkingSlot.objects.filter(is_available=False).count()
    total_bookings = Booking.objects.count()
    active_bookings = Booking.objects.filter(status='Active').count()
    recent_bookings = Booking.objects.all().order_by('-booking_time')[:10]
    
    # Calculate total revenue
    total_revenue = Booking.objects.filter(status='Active').aggregate(Sum('total_price'))['total_price__sum'] or 0
    completed_revenue = Booking.objects.filter(status='Cancelled').aggregate(Sum('total_price'))['total_price__sum'] or 0
    
    return render(request, 'admin_dashboard.html', {
        'total_slots': total_slots,
        'available_slots': available_slots,
        'occupied_slots': occupied_slots,
        'total_bookings': total_bookings,
        'active_bookings': active_bookings,
        'recent_bookings': recent_bookings,
        'total_revenue': total_revenue,
        'completed_revenue': completed_revenue,
    })

@staff_member_required
def manage_slots(request):
    slots = ParkingSlot.objects.all().order_by('slot_number')
    return render(request, 'manage_slots.html', {'slots': slots})

@staff_member_required
def add_slot(request):
    if request.method == 'POST':
        slot_number = request.POST.get('slot_number')
        price_per_hour = request.POST.get('price_per_hour', 50.00)
        ParkingSlot.objects.create(slot_number=slot_number, price_per_hour=price_per_hour)
        messages.success(request, f'Slot {slot_number} added successfully with price BDT {price_per_hour}/hour!')
    return redirect('manage_slots')

@staff_member_required
def delete_slot(request, slot_id):
    if request.method == 'POST':
        slot = ParkingSlot.objects.get(id=slot_id)
        slot.delete()
        messages.success(request, 'Slot deleted successfully!')
    return redirect('manage_slots')

@staff_member_required
def edit_slot(request, slot_id):
    slot = ParkingSlot.objects.get(id=slot_id)
    if request.method == 'POST':
        slot.slot_number = request.POST.get('slot_number', slot.slot_number)
        slot.price_per_hour = request.POST.get('price_per_hour', slot.price_per_hour)
        slot.save()
        messages.success(request, f'Slot {slot.slot_number} updated successfully!')
        return redirect('manage_slots')
    
    return render(request, 'edit_slot.html', {'slot': slot})

@staff_member_required
def all_bookings(request):
    bookings = Booking.objects.all().order_by('-booking_time')
    return render(request, 'all_bookings.html', {'bookings': bookings})

@staff_member_required
def admin_cancel_booking(request, booking_id):
    if request.method == 'POST':
        booking = Booking.objects.get(id=booking_id)
        booking.status = 'Cancelled'
        booking.slot.is_available = True
        booking.slot.save()
        booking.save()
        messages.success(request, 'Booking cancelled successfully!')
    return redirect('all_bookings')
