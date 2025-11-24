from django.db import models

# Create your models here.

class Region(models.Model):
    id_region = models.AutoField(primary_key=True, unique=True)
    nombre = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.nombre


class Pais(models.Model):
    id_pais = models.AutoField(primary_key=True, unique=True)
    nombre = models.CharField(max_length=50, unique=True)
    id_region = models.ForeignKey(Region, on_delete=models.CASCADE)
    happiness_score = models.DecimalField(max_digits=6, decimal_places=5)
    standard_error = models.DecimalField(max_digits=6, decimal_places=5)
    economy = models.DecimalField(max_digits=6, decimal_places=5)
    family = models.DecimalField(max_digits=6, decimal_places=5)
    health = models.DecimalField(max_digits=6, decimal_places=5)
    freedom = models.DecimalField(max_digits=6, decimal_places=5)
    trust = models.DecimalField(max_digits=6, decimal_places=5)
    generosity = models.DecimalField(max_digits=6, decimal_places=5)
    dystopia = models.DecimalField(max_digits=6, decimal_places=5)

    def __str__(self):
        return f"{self.nombre}"
