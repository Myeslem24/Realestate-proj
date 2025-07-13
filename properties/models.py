from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# مدير المستخدمين
class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, email=None, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('رقم الهاتف مطلوب')
        user = self.model(phone_number=phone_number, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(phone_number, email, password, **extra_fields)

# نموذج المستخدم
class CustomUser(AbstractBaseUser, PermissionsMixin):
    phone_number = models.CharField(max_length=15, unique=True)
    name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    city = models.CharField(max_length=100)
    email = models.EmailField(unique=True, null=True, blank=True)

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['name']

    objects = CustomUserManager()

    def __str__(self):
        return self.phone_number

# نموذج العقار
class Property(models.Model):
    PROPERTY_TYPES = [
        ('house', 'منزل'),
        ('apartment', 'شقة'),
        ('land', 'قطعة أرض'),
    ]

    PURPOSE_CHOICES = [
        ('sale', 'للبيع'),
        ('rent', 'للإيجار'),
    ]

    STATUS = [
        ('pending', 'في انتظار المراجعة'),
        ('approved', 'مقبول'),
        ('rejected', 'مرفوض'),
    ]

    MAIN_LOCATIONS = [
        ('نواكشوط', 'نواكشوط'),
        ('نواذيبو', 'نواذيبو'),
        ('كيفة', 'كيفة'),
        ('لعيون', 'لعيون'),
        ('زويرات', 'زويرات'),
        ('النعمة', 'النعمة'),
    ]

    NAWAKCHOTT_DISTRICTS = [
        ('تفرغ زينة', 'تفرغ زينة'),
        ('دار النعيم', 'دار النعيم'),
        ('لكصر', 'لكصر'),
        ('الميناء', 'الميناء'),
        ('السبخة', 'السبخة'),
        ('تيارت', 'تيارت'),
        ('الرياض', 'الرياض'),
        ('عرفات', 'عرفات'),
        ('توجونين', 'توجونين'),
    ]

    PAYMENT_METHODS = [
        ('fixed', 'مبلغ ثابت'),
        ('commission', 'عمولة'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=PROPERTY_TYPES)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    main_image = models.ImageField(upload_to='property_main/', blank=True, null=True)
    video = models.FileField(upload_to='property_videos/', blank=True, null=True)
    main_location = models.CharField(max_length=50, choices=MAIN_LOCATIONS)
    district = models.CharField(max_length=50, choices=NAWAKCHOTT_DISTRICTS, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS, default='pending')
    is_sold = models.BooleanField(default=False)
    owner = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='properties')
    created_at = models.DateTimeField(auto_now_add=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.get_type_display()} - {self.get_purpose_display()}"

class PropertyMedia(models.Model):
    property = models.ForeignKey(Property, related_name='media', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='property_images/')  # بدون null و blank

    def __str__(self):
        return f"صورة إضافية لعقار {self.property.title}"
class PaymentProof(models.Model):
    PAYMENT_APPS = [
        ('bankily', 'بنكيلي'),
        ('seddad', 'السداد'),
        ('bimbank', 'بيم بانك'),
        ('masrefy', 'مصرفي'),
    ]

    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='payment_proof')
    app_used = models.CharField(max_length=20, choices=PAYMENT_APPS)
    screenshot = models.ImageField(upload_to='payment_screenshots/')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"إثبات دفع لـ {self.property.title} عبر {self.get_app_used_display()}"

