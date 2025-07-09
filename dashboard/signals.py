from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Seat, Showtime


@receiver(post_save, sender=Showtime)
def create_seats_for_showtime(sender, instance, created, **kwargs):
    if created:
        rows = ['A', 'B', 'C','D','E','F','G','H','I','J']
        for row in rows:
            for col in range(1, 10):
                seat_number = f"{row}{col}"
                Seat.objects.create(showtime=instance, seat_number=seat_number)
