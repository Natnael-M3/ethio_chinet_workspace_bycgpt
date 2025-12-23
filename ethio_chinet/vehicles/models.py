from django.db import models

class VehicleType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class LoadType(models.Model):
    name = models.CharField(max_length=50, unique=True)  # solid / liquid

    def __str__(self):
        return self.name


class Vehicle(models.Model):
    plate_number = models.CharField(max_length=50, unique=True)

    vehicle_type = models.ForeignKey(
        VehicleType, on_delete=models.PROTECT
    )

    load_type = models.ForeignKey(
        LoadType, on_delete=models.PROTECT
    )

    capacity_kg = models.DecimalField(max_digits=10, decimal_places=2)
    region = models.CharField(max_length=100)
    code = models.CharField(max_length=50)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.plate_number
    vehicle_type = models.CharField(max_length=100)
    load_type = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.vehicle_type} - {self.load_type}"