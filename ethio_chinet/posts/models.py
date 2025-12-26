from django.db import models
from django.utils import timezone

class Post(models.Model):
    STATUS_CHOICES = (
        ('posted', 'Posted'),
        ('taken', 'Taken'),
        ('finished', 'Finished'),
    )

    post_code = models.CharField(max_length=6, db_index=True, editable=False)

    customer = models.ForeignKey(
        'users.User',
        related_name='customer_posts',
        on_delete=models.CASCADE
    )

    driver = models.ForeignKey(
        'users.User',
        related_name='driver_posts',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    assigned_admin = models.ForeignKey(
        'users.User',
        related_name='admin_posts',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    pickup_location = models.ForeignKey(
        'locations.Location',
        related_name='pickup_posts',
        on_delete=models.PROTECT
    )

    dropoff_location = models.ForeignKey(
        'locations.Location',
        related_name='dropoff_posts',
        on_delete=models.PROTECT
    )

    vehicle_type = models.ForeignKey(
        'vehicles.VehicleType',
        on_delete=models.PROTECT
    )

    load_type = models.ForeignKey(
        'vehicles.LoadType',
        on_delete=models.PROTECT
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='posted'
    )

    current_latitude = models.FloatField(null=True, blank=True)
    current_longitude = models.FloatField(null=True, blank=True)
    location_updated_at = models.DateTimeField(null=True, blank=True)
    required_date = models.DateTimeField()
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_expired(self):
        return self.expires_at <= timezone.now()

    def __str__(self):
        return self.post_code
