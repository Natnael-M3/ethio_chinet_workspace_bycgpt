from django.db import models

class DriverRating(models.Model):
    driver = models.OneToOneField(
        "users.User",
        on_delete=models.CASCADE,
        related_name="rating",
    )
    completed_deliveries = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=0.0)

    def recalculate(self):
        # simple logic: each finished post adds 1 star up to 5
        self.completed_deliveries += 1
        self.rating = min(5.0, self.completed_deliveries)
        self.save()
