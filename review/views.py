from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Review
from parking.models import Booking

# Create your views here.

@login_required(login_url='/login/')
def submit_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    # Check if review already exists for this booking
    if Review.objects.filter(booking=booking).exists():
        messages.info(request, 'You have already submitted a review for this booking.')
        return redirect('my_bookings')
    
    if request.method == 'POST':
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        
        if rating:
            Review.objects.create(
                user=request.user,
                booking=booking,
                rating=int(rating),
                comment=comment or ''
            )
            messages.success(request, 'Thank you for your review!')
            return redirect('my_bookings')
        else:
            messages.error(request, 'Please select a rating.')
    
    return render(request, 'review_form.html', {'booking': booking})

def all_reviews(request):
    reviews = Review.objects.select_related('user', 'booking', 'booking__vehicle').order_by('-created_at')
    return render(request, 'reviews.html', {'reviews': reviews})
