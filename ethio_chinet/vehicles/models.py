from django.db import models
from django.conf import settings
# ✅ Correct
from loadtypes.models import LoadType

class VehicleType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class VehicleRegion(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class VehicleCode(models.Model):
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.code


# ✅ Admin can add LoadTypes like "solid", "liquid"
# class LoadType(models.Model):
#     name = models.CharField(max_length=50, unique=True)

#     def __str__(self):
#         return self.name


class Vehicle(models.Model):
    plate_number = models.CharField(max_length=50)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.PROTECT)
    vehicle_region = models.ForeignKey(VehicleRegion, on_delete=models.PROTECT)
    vehicle_code = models.ForeignKey(VehicleCode, on_delete=models.PROTECT)
    load_type = models.ForeignKey(
        LoadType,
        on_delete=models.PROTECT
    )
    capacity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    driver = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vehicles",
        null = True,
        blank = True
    )
    is_active = models.BooleanField(default=True)
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["vehicle_region", "vehicle_code", "plate_number"],
                name="unique_plate_per_region_code"
            )
        ]

    def __str__(self):
        return f"{self.plate_number} - {self.vehicle_type.name}"
