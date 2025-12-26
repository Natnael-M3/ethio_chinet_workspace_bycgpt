from django.db import models

class Location(models.Model):
    location_name = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return self.location_name
