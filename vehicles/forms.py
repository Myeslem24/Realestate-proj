from django import forms
from .models import Vehicle
from django.forms import modelformset_factory
from .models import Vehicle, VehicleMedia
from django.core.validators import FileExtensionValidator
from .models import VehiclePaymentProof

class VehicleForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['brand', 'model', 'year', 'fuel_type', 'condition', 'purpose', 'price', 'image', 'video', 'description']
        widgets = {
            'brand': forms.Select(attrs={'class': 'form-control', 'id': 'id_brand'}),
            'model': forms.Select(attrs={'class': 'form-control', 'id': 'id_model'}),
            'year': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1980,
                'max': 2050,
                'placeholder': 'سنة الصنع'
            }),
            'fuel_type': forms.Select(attrs={'class': 'form-control'}),
            'condition': forms.Select(attrs={'class': 'form-control'}),
            'purpose': forms.Select(attrs={'class': 'form-control'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مثال: 1200000'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'video': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'أدخل وصف السيارة'}),
        }
VehicleMediaFormSet = modelformset_factory(
    VehicleMedia,
    fields=('image',),
    extra=3,
    max_num=3,
    widgets={
        'image': forms.ClearableFileInput(attrs={'class': 'form-control'})
    }
)
class VehiclePaymentProofForm(forms.ModelForm):
    class Meta:
        model = VehiclePaymentProof
        fields = ['app_used', 'screenshot']
        labels = {
            'app_used': 'التطبيق المستخدم للدفع',
            'screenshot': 'لقطة شاشة الدفع',
        }
        widgets = {
            'app_used': forms.Select(attrs={'class': 'form-select'}),
            'screenshot': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

