from django.urls import path
from .views import (
    review_vehicles,
    approve_vehicle,
    reject_vehicle,
    edit_vehicle,
    add_vehicle,
    vehicle_list,
    get_models_by_brand,
    delete_vehicle,  # ✅ أضفه هنا
)
from .views import vehicle_detail
urlpatterns = [
    path('ajax/get-models/', get_models_by_brand, name='get_car_models'),
    path('admin/review-vehicles/', review_vehicles, name='review_vehicles'),
    path('admin/approve-vehicle/<int:pk>/', approve_vehicle, name='approve_vehicle'),
    path('admin/reject-vehicle/<int:pk>/', reject_vehicle, name='reject_vehicle'),
    path('edit/<int:pk>/', edit_vehicle, name='edit_vehicle'),
    path('add/', add_vehicle, name='add_vehicle'),
    path('', vehicle_list, name='vehicle_list'),
    path('delete/<int:pk>/', delete_vehicle, name='delete_vehicle'),
    path('<int:pk>/', vehicle_detail, name='vehicle_detail'),
]
