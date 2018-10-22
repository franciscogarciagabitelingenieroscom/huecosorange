from django.db import models

# Create your models here.


from django.contrib.auth.models import AbstractUser
from django.conf import settings
class User(AbstractUser):
    pass






class Actuacion (models.Model):



    municipio = models.CharField(max_length=50, help_text="Población")
    actuacion = models.CharField(max_length=25, help_text="Código Actuación", unique=True)
    idzona = models.CharField(max_length=10, help_text="ID de Zona")
    preparado_por = models.ForeignKey(settings.AUTH_USER_MODEL, to_field="username", on_delete=models.CASCADE, null=True, related_name='actuaciones_preparadas')
    preparado_fecha = models.DateField(help_text="Fecha Preparado", null=True)
    is_preparado = models.BooleanField(default=False)
    replanteado_por = models.ForeignKey(settings.AUTH_USER_MODEL, to_field="username",on_delete=models.CASCADE, null=True, related_name='actuaciones_replanteadas')
    replanteado_fecha = models.DateField(help_text="Fecha Replanteado", null=True)
    is_replanteado = models.BooleanField(default=False)
    aaii_por = models.ForeignKey(settings.AUTH_USER_MODEL, to_field="username", on_delete=models.CASCADE, null=True, related_name='actuaciones_aaii_realizadas')
    aaii_fecha = models.DateField( help_text="Fecha Realización AAII", null=True)
    is_aaii_preparada = models.BooleanField(default=False)

    class Meta:
        ordering = ["actuacion"]
        verbose_name = "Actuación"
        verbose_name_plural = "Actuaciones"
    def __str__(self):
        return  self.actuacion


class Finca (models.Model):
    NO_PROCEDE = 'NO PROCEDE'
    CONSULTA = 'CONSULTA'
    OK = 'OK'


    VIABLE = 'VIABLE'
    NO_VIABLE = 'NO VIABLE'
    REPLANTEAR = 'VOLVER A REPLANTEAR'
    TRAMO3 = 'TRAMO 3'
    INCIDENCIA = 'INCIDENCIA'
    PREPARADO = 'PREPARADO'



    CTO_LEJOS = 'CTO A +120m'
    CTO_SATURADA = 'CTO SATURADA'
    YA_EN_CT = 'DIRECCION REFLEJADA EN COBERTURA TOTAL'
    NO_EXISTE = 'NO EXISTE FINCA'
    SOLAR = 'SOLAR'
    OTRA_ACTUACION = 'PERTENECE A OTRA ACTUACIÓN'
    SIN_DOCS = 'SIN DOCUMENTOS'
    OTROS= 'OTROS'
    SIN_CTO = 'CTO NO INSTALADA'



    COMENTARIO_GABITEL_CHOICES = (
        (CTO_LEJOS , 'CTO A +120m'),
        (CTO_SATURADA , 'CTO SATURADA'),
        (YA_EN_CT , 'DIRECCION REFLEJADA EN COBERTURA TOTAL'),
        (NO_EXISTE , 'NO EXISTE FINCA'),
        (SOLAR , 'SOLAR'),
        (OTRA_ACTUACION , 'PERTENECE A OTRA ACTUACIÓN'),
        (SIN_DOCS , 'SIN DOCUMENTOS'),
        (OTROS, 'OTROS'),
        (SIN_CTO , 'CTO NO INSTALADA'),

    )

    RESULTADO_PREPARACION_CHOICES = (
        (PREPARADO , 'PREPARADO'),
        (NO_VIABLE, 'NO VIABLE'),
        (CONSULTA, 'CONSULTA'),
        (NO_PROCEDE, 'NO PROCEDE'),
        (TRAMO3, 'TRAMO 3'),
        (INCIDENCIA, 'INCIDENCIA'),
    )

    RESULTADO_REPLANTEO_CHOICES = (
        (VIABLE, 'VIABLE'),
        (NO_VIABLE, 'NO VIABLE'),
        (CONSULTA, 'CONSULTA'),
        (NO_PROCEDE, 'NO PROCEDE'),
        (REPLANTEAR, 'VOLVER A REPLANTEAR'),
        (TRAMO3, 'TRAMO 3'),
        (INCIDENCIA, 'INCIDENCIA'),
    )

    RESULTADO_AAII_CHOICES = (
            (NO_PROCEDE , 'NO PROCEDE'),
            (CONSULTA , 'CONSULTA'),
            (OK , 'OK'),
    )

    actuacion =  models.ForeignKey(Actuacion, to_field="actuacion", on_delete=models.CASCADE, null=True)
    gescal17 = models.CharField(max_length=17, help_text="GESCAL17", default="")
    ref_parcela = models.CharField(max_length=14, help_text="Código Catastral")
    nombre_via = models.CharField(max_length=200, help_text="Nombre Vía")
    numero_via = models.CharField( max_length=5, help_text="Número Vía")
    numero_uuii = models.IntegerField( help_text="Número de UUII")
    observaciones = models.CharField(max_length=200, help_text="Observaciones")
    numero_uuii_definitivo = models.IntegerField(null=True, help_text="Número de UUII definitivas")
    resultado_preparacion  = models.CharField(max_length=50, help_text="Resultado Preparación", null=True, choices=RESULTADO_PREPARACION_CHOICES)
    resultado_replanteo  = models.CharField(max_length=50, help_text="Resultado Replanteo", null=True, choices=RESULTADO_REPLANTEO_CHOICES)
    estado_aaii  = models.CharField(max_length=50, help_text="Estado AAII", null=True, choices=RESULTADO_AAII_CHOICES)
    comentario_gabitel = models.CharField(max_length=100, help_text="Comentario Gabitel", null=True, choices=COMENTARIO_GABITEL_CHOICES)
    aclaraciones  = models.TextField(help_text="Comentario Gabitel", null=True)
    is_replanteado = models.BooleanField(default=False)


    class Meta:
        ordering = ["nombre_via", "numero_via"]
        verbose_name_plural = "Fincas"
    def __str__(self):
            return self.actuacion.actuacion + " " + self.nombre_via + " " + self.numero_via + " " + self.gescal17
    def catastroLink(self):
        link = "https://www1.sedecatastro.gob.es/Cartografia/mapa.aspx?refcat="
        return link  + self.ref_parcela
