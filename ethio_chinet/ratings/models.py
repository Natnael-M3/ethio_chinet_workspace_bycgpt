from django.db import models

class DriverRating(models.Model):
    driver = models.OneToOneField(
        'users.User',
        on_delete=models.CASCADE
    )

    success_rate = models.DecimalField(
        max_digits=5, decimal_places=2, default=0
    )

    last_updated = models.DateTimeField(auto_now=True)
