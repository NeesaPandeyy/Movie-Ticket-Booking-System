from django.urls import path

from . import views
from .views import KhaltiVerifyView

app_name = "dashboard"

urlpatterns = [
    path("", views.MovieListView.as_view(), name="movie-list"),
    path("showtimes/<int:movie_id>/", views.ShowtimeListView.as_view(), name="showtime-list"),
    path("book/<int:showtime_id>/", views.BookingCreateView.as_view(), name="book-seats"),
    path("booking/confirm/", views.BookingConfirmView.as_view(), name="booking-confirm"),
    path("booking/payment-choice/", views.BookingPaymentChoiceView.as_view(), name="booking-payment-choice"),
    path("booking/qr/<int:booking_id>/", views.BookingQRView.as_view(), name="booking-qr"),
    path("booking/online/", views.OnlinePaymentView.as_view(), name="online-payment"),
    path("bookings/", views.UserBookingListView.as_view(), name="user-bookings"),
    path("booking/cancel/<int:booking_id>/", views.BookingCancelView.as_view(), name="cancel-booking"),
    path('khalti/verify/', KhaltiVerifyView.as_view(), name='khalti_verify'),

]
