from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import TravelOption, Booking
from django.utils import timezone
from django.db import models

# Home - List all travel options
def home(request):
    travels = TravelOption.objects.all()
    travel_type = request.GET.get('type')
    source = request.GET.get('source')
    destination = request.GET.get('destination')
    date = request.GET.get('date')
    search_query = request.GET.get('search')

    # Apply filters
    if travel_type:
        travels = travels.filter(type=travel_type)
    if source:
        travels = travels.filter(source__icontains=source)
    if destination:
        travels = travels.filter(destination__icontains=destination)
    if date:
        travels = travels.filter(date_time__date=date)
    
    # Apply search across multiple fields
    if search_query:
        travels = travels.filter(
            models.Q(source__icontains=search_query) |
            models.Q(destination__icontains=search_query) |
            models.Q(type__icontains=search_query)
        )

    # Order by date (earliest first)
    travels = travels.order_by('date_time')

    context = {
        'travels': travels,
        'filters': {
            'type': travel_type or '',
            'source': source or '',
            'destination': destination or '',
            'date': date or '',
            'search': search_query or '',
        }
    }
    return render(request, 'bookings/home.html', context)

# Book a ticket
@login_required
def book_travel(request, travel_id):
    travel = get_object_or_404(TravelOption, travel_id=travel_id)
    
    # Check if travel is in the past
    if travel.date_time < timezone.now():
        messages.error(request, 'Cannot book travel options in the past.')
        return redirect('home')
    
    if request.method == "POST":
        try:
            seats = int(request.POST.get('seats', '0'))
        except ValueError:
            seats = 0
            
        # Enhanced validation
        if seats < 1:
            messages.error(request, 'Please enter a valid number of seats (minimum 1).')
        elif seats > travel.available_seats:
            messages.error(request, f'Only {travel.available_seats} seats available. Please select fewer seats.')
        elif seats > 10:  # Reasonable limit
            messages.error(request, 'Maximum 10 seats can be booked at once.')
        else:
            # Double-check availability (in case of concurrent bookings)
            travel.refresh_from_db()
            if travel.available_seats >= seats:
                total_price = seats * travel.price
                Booking.objects.create(
                    user=request.user,
                    travel_option=travel,
                    number_of_seats=seats,
                    total_price=total_price,
                    booking_date=timezone.now()
                )
                travel.available_seats -= seats
                travel.save()
                messages.success(request, f'Booking confirmed! {seats} seat(s) booked for ₹{total_price}')
                return redirect('my_bookings')
            else:
                messages.error(request, 'Seats no longer available. Please try again.')
    
    return render(request, 'bookings/book.html', {'travel': travel})

# View bookings
@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-booking_date')
    current = bookings.filter(status='Confirmed')
    past = bookings.exclude(status='Confirmed')
    return render(request, 'bookings/my_bookings.html', {'current': current, 'past': past})

# Cancel booking
@login_required
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id)
    if booking.status != 'Cancelled':
        booking.status = 'Cancelled'
        booking.save()
        # restore seats
        travel = booking.travel_option
        travel.available_seats += booking.number_of_seats
        travel.save()
        messages.info(request, 'Booking cancelled.')
    return redirect('my_bookings')

# Registration
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Registration successful. You can now log in.')
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Simple profile update (first/last name and email)
@login_required
def profile(request):
    user: User = request.user
    if request.method == 'POST':
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        messages.success(request, 'Profile updated.')
        return redirect('profile')
    return render(request, 'registration/profile.html', {'user': user})
