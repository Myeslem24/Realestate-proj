from django import forms
from django.forms import modelformset_factory
from .models import Property, PropertyMedia, CustomUser
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import FileExtensionValidator
from .models import PaymentProof

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

class PropertyForm(forms.ModelForm):
    main_location = forms.ChoiceField(
        choices=MAIN_LOCATIONS,
        label='المدينة',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    district = forms.ChoiceField(
        choices=NAWAKCHOTT_DISTRICTS,
        required=False,
        label='المقاطعة',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    latitude = forms.FloatField(
        required=False,
        label='خط العرض (Latitude)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مثال: 18.0735'})
    )
    longitude = forms.FloatField(
        required=False,
        label='خط الطول (Longitude)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مثال: -15.9582'})
    )

    class Meta:
        model = Property
        fields = ['title', 'description', 'type', 'purpose', 'price', 'main_location', 'district',
                  'latitude', 'longitude', 'is_sold', 'main_image', 'video']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'عنوان العقار'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'أدخل وصفًا للعقار...'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مثال: 100000'}),
            'type': forms.Select(attrs={'class': 'form-control'}),
            'purpose': forms.Select(attrs={'class': 'form-control'}),
            'is_sold': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'main_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'video': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class PropertyMediaForm(forms.ModelForm):
    class Meta:
        model = PropertyMedia
        fields = ['image']
        widgets = {
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

PropertyMediaFormSet = modelformset_factory(
    PropertyMedia,
    form=PropertyMediaForm,
    fields=['image'],
    extra=3
)

class CustomUserCreationForm(UserCreationForm):
    name = forms.CharField(label='الاسم الكامل', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone_number = forms.CharField(label='رقم الهاتف', max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.CharField(label='المدينة', max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ('name', 'phone_number', 'email', 'password1', 'password2')
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }

class LoginForm(forms.Form):
    identifier = forms.CharField(label="رقم الهاتف أو البريد الإلكتروني", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="كلمة المرور")
class PaymentProofForm(forms.ModelForm):
    class Meta:
        model = PaymentProof
        fields = ['app_used', 'screenshot']
        labels = {
            'app_used': 'اختر التطبيق المستخدم',
            'screenshot': '📸 لقطة الشاشة'
        }
        widgets = {
            'app_used': forms.Select(attrs={'class': 'form-select'}),
            'screenshot': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

