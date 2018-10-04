from django.db import models

# Create your models here.
class Ciudad (models.Model):
    nombre = models.CharField(max_length=100, help_text="")

    class Meta:
        verbose_name_plural = "Ciudades"
class DireccionEnCobertura(models.Model):
    gescal17 = models.CharField(max_length=17, help_text="")
    municipio = models.CharField(max_length=50, help_text="")
    tipo_via = models.CharField(max_length=50, help_text="")
    nombre_via = models.CharField(max_length=200, help_text="")
    numero = models.CharField( max_length=5, help_text="", null=True)
    cod_postal = models.CharField( max_length=5, help_text="")
    uuii = models.CharField( max_length=5, help_text="", null=True)

    class Meta:
        ordering = ["tipo_via", "nombre_via", "numero"]
        verbose_name_plural = "DireccionesEnCobertura"



    def __str__(self):
        return self.municipio + " " + self.tipo_via + " " + self.nombre_via + " " + str( self.numero )

    def googleMapsLink(self):
        link = "https://www.google.com/maps/search/?api=1&query="
        return link  + self.tipo_via.replace(" ", "%20") + "%20" + self.nombre_via.replace(" ", "%20") + "%2C" + str( self.numero ) + "%2C" + self.cod_postal + "%2C" +  self.municipio
