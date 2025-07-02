from django.db import models
from properties.models import CustomUser
from django.core.validators import MinValueValidator, MaxValueValidator
import datetime

# الشركة
class CarBrand(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# الطراز
class CarModel(models.Model):
    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE, related_name='models')
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.brand.name} {self.name}"

# السيارة
class Vehicle(models.Model):
    FUEL_TYPES = [
        ('gasoline', 'بنزين'),
        ('diesel', 'ديزل'),
        ('hybrid', 'هايبرد'),
        ('electric', 'كهرباء'),
    ]
    CONDITION_CHOICES = [
        ('new', 'جديدة'),
        ('used', 'مستعملة'),
    ]
    PURPOSE_CHOICES = [
        ('sale', 'للبيع'),
        ('rent', 'للإيجار'),
    ]
    STATUS_CHOICES = [
        ('pending', 'قيد المراجعة'),
        ('approved', 'مقبولة'),
        ('rejected', 'مرفوضة'),
    ]

    brand = models.ForeignKey(CarBrand, on_delete=models.CASCADE, verbose_name="الشركة")
    model = models.ForeignKey(CarModel, on_delete=models.CASCADE, verbose_name="الطراز")
    year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1980),
            MaxValueValidator(datetime.datetime.now().year + 1)
        ],
        verbose_name="سنة الصنع"
    )
    image = models.ImageField(upload_to='vehicles/images/', verbose_name="صورة", null=True, blank=True)
    video = models.FileField(upload_to='vehicles/videos/', verbose_name="فيديو", null=True, blank=True)
    description = models.TextField(verbose_name="الوصف", null=True, blank=True)
    fuel_type = models.CharField(max_length=10, choices=FUEL_TYPES, verbose_name="نوع الوقود")
    condition = models.CharField(max_length=10, choices=CONDITION_CHOICES, verbose_name="الحالة")
    purpose = models.CharField(max_length=10, choices=PURPOSE_CHOICES, verbose_name="الغرض")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="السعر")
    owner = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="حالة الطلب"
    )

    def __str__(self):
        return f"{self.brand.name} {self.model.name} ({self.year})"

class VehicleMedia(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='media')
    image = models.ImageField(upload_to='vehicles/extra_images/', null=True, blank=True)

    def __str__(self):
        return f"صورة إضافية لـ {self.vehicle}"
