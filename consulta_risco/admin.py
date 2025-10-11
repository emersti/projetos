from django.contrib import admin
from .models import Estado, Cidade


@admin.register(Estado)
class EstadoAdmin(admin.ModelAdmin):
    list_display = ['nome', 'sigla']
    search_fields = ['nome', 'sigla']


@admin.register(Cidade)
class CidadeAdmin(admin.ModelAdmin):
    list_display = ['nome', 'estado']
    list_filter = ['estado']
    search_fields = ['nome', 'estado__nome']













