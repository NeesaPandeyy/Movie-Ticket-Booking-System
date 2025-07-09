from django.conf import settings
from django.db import models
from django.utils import timezone


class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    duration = models.PositiveIntegerField(help_text="Duration in minutes")
    genre = models.CharField(max_length=50)
    release_date = models.DateField()
    poster = models.ImageField(upload_to='posters/', null=True, blank=True) 


    def __str__(self):
        return self.title


class Showtime(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    starting_time = models.DateTimeField()
    
    def __str__(self):
        local_time = timezone.localtime(self.starting_time)
        return f"{self.movie.title} - {local_time.strftime('%b %d, %Y at %I:%M %p')}"

    @property
    def total_seats(self):
        return 90

    @property
    def available_seats(self):
        return self.seat_set.filter(is_booked=False).count()

class Seat(models.Model):
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    seat_number = models.CharField(max_length=5)  
    is_booked = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.seat_number} ({'Booked' if self.is_booked else 'Available'})"

class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    showtime = models.ForeignKey(Showtime, on_delete=models.CASCADE)
    seats = models.ManyToManyField(Seat)
    booked_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)
    khalti_pidx = models.CharField(max_length=100, blank=True, null=True)
    canceled = models.BooleanField(default=False)


    @property
    def total_amount_paisa(self):
        return int(self.seats.count() * 300 * 100)  
    
    def seats_count(self):
        return self.seats.count()

    def __str__(self):
        return f"{self.user.username} - {self.showtime} - {self.seats.count()} seats"
