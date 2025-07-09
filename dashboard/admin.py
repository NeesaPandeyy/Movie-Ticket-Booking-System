from django.contrib import admin

from .models import Booking, Movie, Seat, Showtime

admin.site.site_header = "Movie Booking"



@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'genre', 'duration', 'release_date')
    search_fields = ('title', 'genre')
    list_filter = ('genre', 'release_date')

@admin.register(Showtime)
class ShowtimeAdmin(admin.ModelAdmin):
    list_display = ('movie', 'starting_time', 'available_seats')
    list_filter = ('movie', 'starting_time')
    search_fields = ('movie__title',)

class SeatInline(admin.TabularInline):
    model = Seat
    extra = 0
    readonly_fields = ('seat_number', 'is_booked')
    can_delete = False
    show_change_link = True

@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ('seat_number', 'showtime', 'is_booked')
    list_filter = ('showtime__movie__title', 'is_booked')
    search_fields = ('seat_number', 'showtime__movie__title')
    autocomplete_fields = ("showtime",)

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'showtime', 'booked_at', 'canceled', 'seats_count')
    search_fields = ('showtime',)
    autocomplete_fields = ("showtime",)
    readonly_fields = ('user',) 

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('seats')

    def seats_count(self, obj):
        return obj.seats.count()
    seats_count.short_description = 'Number of Seats'
