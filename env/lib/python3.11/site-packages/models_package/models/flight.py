from django.db import models
from django.utils import timezone
from datetime import timedelta

class FlightLibModel(models.Model):
    number = models.CharField(max_length=20, primary_key=True)
    origin_point = models.CharField(max_length=20)
    destination_point = models.CharField(max_length=20)
    departure_time = models.DateTimeField(default=timezone.now() + timedelta(days=3))
    arrival_time = models.DateTimeField(default=timezone.now() + timedelta(days=3))
    available_seats = models.PositiveSmallIntegerField()
    price = models.FloatField()
    
    is_active = models.BooleanField(default=True)
