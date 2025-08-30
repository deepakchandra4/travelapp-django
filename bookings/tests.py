from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from .models import TravelOption, Booking


class TravelOptionModelTest(TestCase):
    def setUp(self):
        self.travel_option = TravelOption.objects.create(
            type='Flight',
            source='Mumbai',
            destination='Delhi',
            date_time=timezone.now() + timedelta(days=7),
            price=5000.00,
            available_seats=50
        )

    def test_travel_option_creation(self):
        """Test that a travel option is created correctly"""
        self.assertEqual(self.travel_option.type, 'Flight')
        self.assertEqual(self.travel_option.source, 'Mumbai')
        self.assertEqual(self.travel_option.destination, 'Delhi')
        self.assertEqual(self.travel_option.price, 5000.00)
        self.assertEqual(self.travel_option.available_seats, 50)

    def test_travel_option_str_representation(self):
        """Test the string representation of travel option"""
        expected_str = "Flight - Mumbai to Delhi"
        self.assertEqual(str(self.travel_option), expected_str)


class BookingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.travel_option = TravelOption.objects.create(
            type='Train',
            source='Bangalore',
            destination='Chennai',
            date_time=timezone.now() + timedelta(days=3),
            price=800.00,
            available_seats=100
        )
        self.booking = Booking.objects.create(
            user=self.user,
            travel_option=self.travel_option,
            number_of_seats=2,
            total_price=1600.00
        )

    def test_booking_creation(self):
        """Test that a booking is created correctly"""
        self.assertEqual(self.booking.user, self.user)
        self.assertEqual(self.booking.travel_option, self.travel_option)
        self.assertEqual(self.booking.number_of_seats, 2)
        self.assertEqual(self.booking.total_price, 1600.00)
        self.assertEqual(self.booking.status, 'Confirmed')

    def test_booking_relationships(self):
        """Test the foreign key relationships"""
        self.assertEqual(self.booking.user.username, 'testuser')
        self.assertEqual(self.booking.travel_option.type, 'Train')


class HomeViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.travel_option = TravelOption.objects.create(
            type='Bus',
            source='Pune',
            destination='Mumbai',
            date_time=timezone.now() + timedelta(days=1),
            price=300.00,
            available_seats=30
        )

    def test_home_view_status_code(self):
        """Test that home view returns 200 status code"""
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_home_view_contains_travel_options(self):
        """Test that home view displays travel options"""
        response = self.client.get(reverse('home'))
        self.assertContains(response, 'Pune')
        self.assertContains(response, 'Mumbai')
        self.assertContains(response, 'Bus')

    def test_home_view_search_functionality(self):
        """Test the search functionality"""
        response = self.client.get(reverse('home'), {'search': 'Pune'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pune')

    def test_home_view_filter_by_type(self):
        """Test filtering by travel type"""
        response = self.client.get(reverse('home'), {'type': 'Bus'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Bus')


class BookingViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.travel_option = TravelOption.objects.create(
            type='Flight',
            source='Delhi',
            destination='Mumbai',
            date_time=timezone.now() + timedelta(days=5),
            price=4000.00,
            available_seats=25
        )

    def test_booking_view_requires_authentication(self):
        """Test that booking view requires user to be logged in"""
        response = self.client.get(reverse('book_travel', args=[self.travel_option.travel_id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_booking_view_authenticated_user(self):
        """Test booking view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('book_travel', args=[self.travel_option.travel_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Delhi')
        self.assertContains(response, 'Mumbai')

    def test_successful_booking(self):
        """Test successful booking creation"""
        self.client.login(username='testuser', password='testpass123')
        initial_seats = self.travel_option.available_seats
        
        response = self.client.post(reverse('book_travel', args=[self.travel_option.travel_id]), {
            'seats': 2
        })
        
        # Check redirect to my_bookings
        self.assertEqual(response.status_code, 302)
        
        # Check that booking was created
        booking = Booking.objects.get(user=self.user, travel_option=self.travel_option)
        self.assertEqual(booking.number_of_seats, 2)
        self.assertEqual(booking.total_price, 8000.00)
        
        # Check that seats were reduced
        self.travel_option.refresh_from_db()
        self.assertEqual(self.travel_option.available_seats, initial_seats - 2)

    def test_booking_validation_insufficient_seats(self):
        """Test booking validation when requesting more seats than available"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('book_travel', args=[self.travel_option.travel_id]), {
            'seats': 100  # More than available
        })
        
        # Should stay on booking page with error
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'seats available')

    def test_booking_validation_invalid_seat_count(self):
        """Test booking validation for invalid seat count"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('book_travel', args=[self.travel_option.travel_id]), {
            'seats': 0
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'valid number of seats')


class MyBookingsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.travel_option = TravelOption.objects.create(
            type='Train',
            source='Mumbai',
            destination='Pune',
            date_time=timezone.now() + timedelta(days=2),
            price=500.00,
            available_seats=50
        )
        self.booking = Booking.objects.create(
            user=self.user,
            travel_option=self.travel_option,
            number_of_seats=1,
            total_price=500.00
        )

    def test_my_bookings_requires_authentication(self):
        """Test that my bookings view requires authentication"""
        response = self.client.get(reverse('my_bookings'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_my_bookings_authenticated_user(self):
        """Test my bookings view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('my_bookings'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Mumbai')
        self.assertContains(response, 'Pune')


class CancelBookingTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.travel_option = TravelOption.objects.create(
            type='Bus',
            source='Delhi',
            destination='Agra',
            date_time=timezone.now() + timedelta(days=3),
            price=600.00,
            available_seats=20
        )
        self.booking = Booking.objects.create(
            user=self.user,
            travel_option=self.travel_option,
            number_of_seats=3,
            total_price=1800.00
        )

    def test_cancel_booking_restores_seats(self):
        """Test that cancelling a booking restores available seats"""
        self.client.login(username='testuser', password='testpass123')
        initial_seats = self.travel_option.available_seats
        
        response = self.client.get(reverse('cancel_booking', args=[self.booking.booking_id]))
        
        # Check redirect
        self.assertEqual(response.status_code, 302)
        
        # Check booking is cancelled
        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, 'Cancelled')
        
        # Check seats are restored
        self.travel_option.refresh_from_db()
        self.assertEqual(self.travel_option.available_seats, initial_seats + 3)


class UserRegistrationTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_registration_view_get(self):
        """Test that registration view loads correctly"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Create account')

    def test_successful_registration(self):
        """Test successful user registration"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'password1': 'testpass123',
            'password2': 'testpass123'
        })
        
        # Should redirect to login
        self.assertEqual(response.status_code, 302)
        
        # Check user was created
        user = User.objects.get(username='newuser')
        self.assertTrue(user.check_password('testpass123'))


class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User',
            email='test@example.com'
        )

    def test_profile_view_requires_authentication(self):
        """Test that profile view requires authentication"""
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

    def test_profile_view_authenticated_user(self):
        """Test profile view for authenticated user"""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test')
        self.assertContains(response, 'User')

    def test_profile_update(self):
        """Test profile information update"""
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(reverse('profile'), {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': 'updated@example.com'
        })
        
        # Should redirect back to profile
        self.assertEqual(response.status_code, 302)
        
        # Check user information was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name')
        self.assertEqual(self.user.email, 'updated@example.com')
