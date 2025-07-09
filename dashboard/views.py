import base64
import json
from io import BytesIO

import qrcode
import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View, generic
from django.views.decorators.csrf import csrf_exempt

from .forms import BookingForm
from .models import Booking, Movie, Seat, Showtime


def finalize_booking(request):
    pending = request.session.get("pending_booking")
    if not pending:
        return None, "No pending booking found."

    showtime = get_object_or_404(Showtime, id=pending["showtime_id"])
    seat_numbers = pending["seat_numbers"]

    seats_to_book = list(Seat.objects.filter(showtime=showtime, seat_number__in=seat_numbers, is_booked=False))

    if len(seats_to_book) != len(seat_numbers):
        return None, "Some seats are already booked."

    for seat in seats_to_book:
        seat.is_booked = True
        seat.save()

    booking = Booking.objects.create(user=request.user, showtime=showtime)
    booking.seats.set(seats_to_book)
    showtime.available_seats -= len(seats_to_book)
    showtime.save()

    del request.session["pending_booking"]

    return booking, None


class MovieListView(generic.ListView):
    model = Movie
    template_name = "dashboard/movie_list.html"
    context_object_name = "movies"

    def get_queryset(self):
        query = self.request.GET.get("q")
        if query:
            return Movie.objects.filter(
                Q(title__icontains=query) | Q(genre__icontains=query)
            ).order_by('-release_date')
        return Movie.objects.all().order_by('-release_date')



class ShowtimeListView(LoginRequiredMixin, generic.ListView):
    model = Showtime
    template_name = "dashboard/showtime_list.html"
    context_object_name = "showtimes"

    def get_queryset(self):
        movie_id = self.kwargs.get("movie_id")
        return Showtime.objects.filter(movie_id=movie_id).order_by("starting_time")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["movie"] = get_object_or_404(Movie, id=self.kwargs.get("movie_id"))
        return context


class BookingCreateView(LoginRequiredMixin, generic.FormView):
    template_name = "dashboard/book_seats.html"
    form_class = BookingForm

    def dispatch(self, request, *args, **kwargs):
        self.showtime = get_object_or_404(Showtime, id=kwargs.get("showtime_id"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["showtime"] = self.showtime
        context["seats"] = Seat.objects.filter(showtime=self.showtime).order_by('seat_number')
        return context

    def form_valid(self, form):
        selected_seats_str = form.cleaned_data["selected_seats"]
        seat_numbers = [s.strip() for s in selected_seats_str.split(",") if s.strip()]

        seats_to_book = list(Seat.objects.filter(showtime=self.showtime, seat_number__in=seat_numbers, is_booked=False))

        if len(seats_to_book) != len(seat_numbers):
            form.add_error(None, "One or more selected seats are already booked. Please select again.")
            return self.form_invalid(form)

        self.request.session["pending_booking"] = {
            "showtime_id": self.showtime.id,
            "seat_numbers": seat_numbers,
        }

        return redirect("dashboard:booking-confirm")


class BookingConfirmView(LoginRequiredMixin, View):
    def get(self, request):
        pending = request.session.get("pending_booking")
        if not pending:
            messages.error(request, "No booking in progress.")
            return redirect("dashboard:movie-list")

        showtime = get_object_or_404(Showtime, id=pending["showtime_id"])
        seats = Seat.objects.filter(showtime=showtime, seat_number__in=pending["seat_numbers"])
        return render(request, "dashboard/booking_confirm.html", {
            "showtime": showtime,
            "seats": seats,
        })

@method_decorator(csrf_exempt, name='dispatch')
class KhaltiVerifyView(View):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            token = data.get("token")
            amount = data.get("amount")

            if not token or not amount:
                return JsonResponse({"success": False, "message": "Token and amount are required."})

            verify_url = "https://dev.khalti.com/api/v2/payment/verify/"
            headers = {
                "Authorization": f"Key {settings.KHALTI_SECRET_KEY}"
            }
            payload = {"token": token, "amount": amount}

            response = requests.post(verify_url, data=payload, headers=headers)

            if response.status_code == 200:
                pending = request.session.get("pending_booking")
                if not pending:
                    return JsonResponse({"success": False, "message": "No pending booking found in session."})

                booking, error = finalize_booking(request)
                if error:
                    return JsonResponse({"success": False, "message": error})

                del request.session["pending_booking"]
                request.session.modified = True

                return JsonResponse({"success": True, "booking_id": booking.id})

            return JsonResponse({"success": False, "message": response.json()})

        except Exception as e:
            return JsonResponse({"success": False, "message": str(e)})


class BookingCancelView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        booking = get_object_or_404(Booking, id=kwargs.get("booking_id"), user=request.user)

        if booking.canceled:
            messages.warning(request, "Booking is already canceled.")
            return redirect("dashboard:user-bookings")

        booking.canceled = True
        booking.save()

        for seat in booking.seats.all():
            seat.is_booked = False
            seat.save()


        messages.success(request, "Booking canceled successfully.")
        return redirect("dashboard:user-bookings")


class UserBookingListView(LoginRequiredMixin, generic.ListView):
    model = Booking
    template_name = "dashboard/user_bookings.html"
    context_object_name = "bookings"

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user, canceled=False).order_by("-booked_at")


class BookingPaymentChoiceView(LoginRequiredMixin, View):
    def post(self, request):
        method = request.POST.get("payment_method")
        pending = request.session.get("pending_booking")
        if not pending:
            messages.error(request, "Booking session expired.")
            return redirect("dashboard:movie-list")

        showtime = get_object_or_404(Showtime, id=pending["showtime_id"])
        seat_numbers = pending["seat_numbers"]

        seats_to_book = list(Seat.objects.filter(showtime=showtime, seat_number__in=seat_numbers, is_booked=False))

        if len(seats_to_book) != len(seat_numbers):
            messages.error(request, "Some seats are no longer available.")
            return redirect("dashboard:book-seats", showtime.id)

        if method == "cash":
            for seat in seats_to_book:
                seat.is_booked = True
                seat.save()

            booking = Booking.objects.create(user=request.user, showtime=showtime)
            booking.seats.set(seats_to_book)

            del request.session["pending_booking"]
            request.session["recent_booking_id"] = booking.id

            return redirect("dashboard:booking-qr", booking_id=booking.id)


        elif method == "online":
            return redirect("dashboard:online-payment")

        messages.error(request, "Invalid payment option.")
        return redirect("dashboard:booking-confirm")


class BookingQRView(LoginRequiredMixin, View):
    def get(self, request, booking_id):
        booking = get_object_or_404(Booking, id=booking_id, user=request.user)

        showtime_date = booking.showtime.starting_time.strftime("%a, %b %d, %Y")
        showtime_time = booking.showtime.starting_time.strftime("%I:%M %p")
        seat_list = ', '.join([seat.seat_number for seat in booking.seats.all()])

        qr_data = (
            f"User: {booking.user.get_full_name() or booking.user.username}\n"
            f"Email: {booking.user.email}\n"
            f"Movie: {booking.showtime.movie.title}\n"
            f"Showtime: {showtime_date}\n"
            f"Time: {showtime_time}\n"
            f"Booking ID: {booking.id}\n"
            f"Seats: {seat_list} (Booked)"
        )

        qr_image = qrcode.make(qr_data)
        buffer = BytesIO()
        qr_image.save(buffer, format="PNG")
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

        return render(request, 'dashboard/booking_qr.html', {
            'booking': booking,
            'qr_code': qr_code_base64,
        })


class OnlinePaymentView(LoginRequiredMixin, View):
    def get(self, request):
        pending = request.session.get("pending_booking")
        if not pending:
            messages.error(request, "No pending booking.")
            return redirect("dashboard:movie-list")

        showtime = get_object_or_404(Showtime, id=pending["showtime_id"])
        seats = Seat.objects.filter(showtime=showtime, seat_number__in=pending["seat_numbers"])
        total_amount = seats.count() * 100
        total_amount_paisa = total_amount * 100

        return render(request, 'dashboard/online_payment.html', {
            'showtime': showtime,
            'seats': seats,
            'total_amount': total_amount,
            'total_amount_paisa': total_amount_paisa,
            'user': request.user
        })

    def post(self, request):
        booking, error = finalize_booking(request)
        if error:
            messages.error(request, error)
            return redirect("dashboard:book-seats", showtime_id=request.session.get("pending_booking", {}).get("showtime_id"))

        if hasattr(booking, 'payment_status'):
            booking.payment_status = "paid"
            booking.save()

        messages.success(request, "Payment successful!")
        return redirect("dashboard:booking-qr", booking_id=booking.id)
