from django.db import models

class LoadType(models.Model):
    name = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Load Type"
        verbose_name_plural = "Load Types"

    def __str__(self):
        return self.name
