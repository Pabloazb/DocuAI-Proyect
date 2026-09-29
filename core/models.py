from django.db import models
from django.contrib.auth.models import User


class TipoDocumento(models.Model):
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True)

    def __str__(self):
        return self.nombre


class Documento(models.Model):
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="documentos"
    )
    formato_documento = models.CharField(max_length=50)
    nombre_documento = models.CharField(max_length=255)
    ruta_documento = models.FileField(
        upload_to="documentos/"
    )
    fecha_subida = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return self.nombre_documento


class Clasificacion(models.Model):
    documento = models.ForeignKey(
        Documento,
        on_delete=models.CASCADE,
        related_name="clasificaciones"
    )

    tipo_documento = models.ForeignKey(
        TipoDocumento,
        on_delete=models.CASCADE,
        related_name="clasificaciones"
    )

    confianza = models.FloatField()
    fecha_clasificacion = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            f"{self.documento} - "
            f"{self.tipo_documento}"
        )