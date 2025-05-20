from django.contrib import admin

# Register your models here.
from .models import DrugSale

@admin.register(DrugSale)
class DrugSaleAdmin(admin.ModelAdmin):
    list_display = ('drug_name', 'atc_code', 'quantity', 'datetime', 'frequency')
    list_filter = ('atc_code', 'frequency', 'datetime')
    search_fields = ('drug_name', 'atc_code')
    ordering = ('-datetime',)