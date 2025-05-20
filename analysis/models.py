from django.db import models

# Create your models here.
class DrugSale(models.Model):
    datetime = models.DateTimeField()
    drug_name = models.CharField(max_length=100)
    quantity = models.IntegerField()
    atc_code = models.CharField(max_length=20)
    frequency = models.CharField(max_length=10,null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    def __str__(self):
        return f"{self.drug_name} in {self.city} on {self.datetime}"
