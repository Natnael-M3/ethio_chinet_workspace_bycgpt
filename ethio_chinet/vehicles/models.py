from django.db import models

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
class LoadType(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    plate_number = models.CharField(max_length=50, unique=True)
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.PROTECT)
    vehicle_region = models.ForeignKey(VehicleRegion, on_delete=models.PROTECT)
    vehicle_code = models.ForeignKey(VehicleCode, on_delete=models.PROTECT)
    load_type = models.ForeignKey(LoadType, on_delete=models.PROTECT)
    capacity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.plate_number} - {self.vehicle_type.name}"
