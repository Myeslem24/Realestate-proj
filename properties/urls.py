# properties/urls.py
from django.urls import path
from . import views
from .views import register_view, we_are_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.property_list, name='property_list'),
    path('add/', views.add_property, name='add_property'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('edit/<int:property_id>/', views.edit_property, name='edit_property'),  # ✅ مضاف حديثاً
    path('delete/<int:property_id>/', views.delete_property, name='delete_property'),
    path('admin/review/', views.review_properties, name='review_properties'),
    path('admin/approve/<int:pk>/', views.approve_property, name='approve_property'),
    path('admin/reject/<int:pk>/', views.reject_property, name='reject_property'),
    path('accounts/register/', register_view, name='register'),
    path('accounts/login/', auth_views.LoginView.as_view(
        redirect_authenticated_user=True,
        template_name='accounts/login.html'
    ), name='login'),
    path('<int:pk>/', views.property_detail, name='property_detail'),
    path('we-are/', we_are_view, name='we_are'),
]

