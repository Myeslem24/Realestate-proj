from django.contrib import admin
from .models import Vehicle, VehicleMedia, CarBrand, CarModel

admin.site.register(VehicleMedia)


@admin.register(CarBrand)
class CarBrandAdmin(admin.ModelAdmin):
    search_fields = ['name']


@admin.register(CarModel)
class CarModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand']
    list_filter = ['brand']
    search_fields = ['name', 'brand__name']


@admin.register(Vehicle)
class VehicleAdmin(admin.ModelAdmin):
    list_display = ['brand', 'model', 'year', 'fuel_type', 'condition', 'purpose', 'price', 'owner', 'created_at']
    list_filter = ['brand', 'year', 'fuel_type', 'condition']
    search_fields = ['model__name', 'brand__name']
