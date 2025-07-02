from django.contrib import admin
from .models import Vehicle
from .models import VehicleMedia
admin.site.register(VehicleMedia)

@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['brand', 'model', 'year', 'fuel_type', 'condition', 'purpose', 'price', 'owner', 'created_at']
    list_filter = ['brand', 'year', 'fuel_type', 'condition']
    search_fields = ['model__name', 'brand__name']

# Register your models here.
