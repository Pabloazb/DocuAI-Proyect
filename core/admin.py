from django.contrib import admin
from .models import (
    Documento,
    TipoDocumento,
    Clasificacion,
)

admin.site.register(Documento)
admin.site.register(TipoDocumento)
admin.site.register(Clasificacion)