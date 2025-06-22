from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Property, PropertyMedia

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('phone_number', 'name', 'is_admin')
    list_filter = ('is_admin',)
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('المعلومات الشخصية', {'fields': ('name',)}),
        ('الصلاحيات', {'fields': ('is_admin', 'is_staff', 'is_superuser')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'name', 'password1', 'password2'),
        }),
    )
    search_fields = ('phone_number',)
    ordering = ('phone_number',)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Property)
admin.site.register(PropertyMedia)

