from django.db import models
from django.conf import settings
import uuid
from luggages.models import Luggage
from loadtypes.models import LoadType
from ratings.models import DriverRating
class Post(models.Model):
    STATUS_CHOICES = [
        ('posted', 'Posted'),
        ('taken', 'Taken'),
        ('finished', 'Finished'),
    ]
    # LOAD_TYPE_CHOICES = [
    #     ('solid', 'Solid'),
    #     ('liquid', 'Liquid'),
    # ]
    luggage = models.ForeignKey(
        Luggage,
        on_delete=models.PROTECT,
        related_name="posts",
        null=True,
        blank=True
    )
    load_type = models.ForeignKey(
        LoadType,
        on_delete=models.PROTECT,
        related_name='posts'
    )
    post_code = models.CharField(max_length=6, unique=True, editable=False)
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    pickup_location = models.ForeignKey('locations.Location', related_name='pickup_posts', on_delete=models.CASCADE)
    dropoff_location = models.ForeignKey('locations.Location', related_name='dropoff_posts', on_delete=models.CASCADE)
    vehicle_type = models.ForeignKey('vehicles.VehicleType', on_delete=models.CASCADE)
    required_date = models.DateTimeField()
    load_type = models.ForeignKey(LoadType, on_delete=models.PROTECT)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='posted')
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_posts')
    assigned_admin = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField( null=True,blank=True)
    def save(self, *args, **kwargs):
        if not self.post_code:
            self.post_code = uuid.uuid4().hex[:6].upper()
        super().save(*args, **kwargs)
