from django.contrib import admin

from .models import Evento, Certificado

# Register your models here.


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('id', 'criador', 'nome', 'data_inicio', 'data_termino')
    prepopulated_fields = {'slug': ('nome',)}


admin.site.register(Certificado)