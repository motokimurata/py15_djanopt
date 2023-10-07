from django.db import models

class WarehouseCapacity(models.Model):
    warehouse_code = models.CharField(max_length=10)
    date = models.DateField()
    capacity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.warehouse_code} - {self.date}"