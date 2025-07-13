from django.shortcuts import render
from django.http import JsonResponse
from .models import CarModel
from vehicles.models import Vehicle  # تأكد من استيراد النموذج
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from .forms import VehicleForm, VehicleMediaFormSet
from django.contrib import messages
from .models import Vehicle, CarBrand, CarModel
from .models import VehicleMedia
from .models import Vehicle, VehiclePaymentProof
from .forms import VehiclePaymentProofForm
import os  # ✅ هذا السطر المهم
from django.conf import settings  # ✅ مهم

def get_models_by_brand(request):
    brand_id = request.GET.get('brand_id')

    if brand_id:
        models = CarModel.objects.filter(brand_id=brand_id).values('id', 'name')
        return JsonResponse(list(models), safe=False)
    else:
        return JsonResponse({'error': 'No brand_id provided'}, status=400)

@login_required
def add_vehicle(request):
    if request.method == 'POST':
        form = VehicleForm(request.POST, request.FILES)
        formset = VehicleMediaFormSet(request.POST, request.FILES, queryset=VehicleMedia.objects.none())

        if form.is_valid() and formset.is_valid():
            vehicle = form.save(commit=False)
            vehicle.owner = request.user
            vehicle.save()

            # حفظ الصور الإضافية
            for media_form in formset:
                if media_form.cleaned_data:
                    media = media_form.save(commit=False)
                    media.vehicle = vehicle
                    media.save()

            messages.success(request, "✅ تم إرسال السيارة.")
            return redirect('choose_vehicle_payment_option', vehicle_id=vehicle.id)
    else:
        form = VehicleForm()
        formset = VehicleMediaFormSet(queryset=VehicleMedia.objects.none())

    return render(request, 'vehicles/add_vehicle.html', {
        'form': form,
        'formset': formset
    })
@login_required
def dashboard(request):
    my_properties = Property.objects.filter(owner=request.user)
    my_vehicles = Vehicle.objects.filter(owner=request.user)

    statuses = [
        ('all', 'الكل'),
        ('pending', 'قيد المراجعة'),
        ('approved', 'مقبول'),
        ('rejected', 'مرفوض'),
    ]

    return render(request, 'dashboard.html', {
        'my_properties': my_properties,
        'my_vehicles': my_vehicles,
        'statuses': statuses,
    })
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    def __str__(self):
        return f"{self.brand} {self.model} {self.year}"

@staff_member_required
def review_vehicles(request):
    pending_vehicles = Vehicle.objects.filter(status='pending')
    return render(request, 'vehicles/review_vehicles.html', {'vehicles': pending_vehicles})
@staff_member_required
def approve_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    vehicle.status = 'approved'
    vehicle.save()
    messages.success(request, "✅ تم قبول السيارة.")
    return redirect('review_vehicles')

@staff_member_required
def reject_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk)
    vehicle.status = 'rejected'
    vehicle.save()
    messages.error(request, "❌ تم رفض السيارة.")
    return redirect('review_vehicles')
@login_required
def edit_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, owner=request.user)

    if request.method == 'POST':
        form = VehicleForm(request.POST, instance=vehicle)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ تم تعديل السيارة بنجاح.")
            return redirect('dashboard')
    else:
        form = VehicleForm(instance=vehicle)

    return render(request, 'vehicles/edit_vehicle.html', {'form': form})

def vehicle_list(request):
    brand_id = request.GET.get('brand')
    model_id = request.GET.get('model')

    vehicles = Vehicle.objects.filter(status='approved')
    brands = CarBrand.objects.all()
    models = CarModel.objects.all()

    if brand_id:
        vehicles = vehicles.filter(brand_id=brand_id)
        models = models.filter(brand_id=brand_id)  # طرازات الشركة فقط

    if model_id:
        vehicles = vehicles.filter(model_id=model_id)

    context = {
        'vehicles': vehicles,
        'brands': brands,
        'models': models,
        'selected_brand': brand_id,
        'selected_model': model_id,
    }
    return render(request, 'vehicles/vehicle_list.html', context)

@login_required
def delete_vehicle(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, owner=request.user)
    vehicle.delete()
    messages.success(request, "🚗 تم حذف السيارة.")
    return redirect('dashboard')

def vehicle_detail(request, pk):
    vehicle = get_object_or_404(Vehicle, pk=pk, status='approved')  # فقط السيارات المقبولة
    return render(request, 'vehicles/vehicle_detail.html', {'vehicle': vehicle})
@login_required
def choose_vehicle_payment_option(request, vehicle_id):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)

    if request.method == "POST":
        option = request.POST.get("payment_option")
        if option == "fixed":
            return redirect('vehicle_payment_instructions', vehicle_id=vehicle_id, method='fixed')
        elif option == "commission":
            return redirect('vehicle_payment_instructions', vehicle_id=vehicle_id, method='commission')

    return render(request, 'vehicles/payment_option.html', {'vehicle': vehicle})


@login_required
def vehicle_payment_instructions(request, vehicle_id, method):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    admin_phone = "22238388780"

    if method == "fixed":
        if request.method == "POST":
            form = PaymentProofForm(request.POST, request.FILES)
            if form.is_valid():
                # احفظ البيانات مؤقتًا داخل حقل screenshot و app_used في نموذج Vehicle
                vehicle.payment_method = "fixed"
                vehicle.payment_app_used = form.cleaned_data['app_used']
                vehicle.screenshot = form.cleaned_data['screenshot']
                vehicle.save()
                messages.success(request, "✅ تم رفع لقطة الدفع بنجاح.")
                return redirect('dashboard')
        else:
            form = PaymentProofForm()

        return render(request, 'vehicles/payment_instructions.html', {
            'vehicle': vehicle,
            'method': method,
            'admin_phone': admin_phone,
            'form': form,
        })

    elif method == "commission":
        if request.method == "POST":
            vehicle.payment_method = "commission"
            vehicle.save()
            return redirect('dashboard')

        return render(request, 'vehicles/payment_instructions.html', {
            'vehicle': vehicle,
            'method': method,
            'admin_phone': admin_phone
        })
@login_required
def vehicle_payment_instructions(request, vehicle_id, method):
    vehicle = get_object_or_404(Vehicle, id=vehicle_id, owner=request.user)
    admin_phone = "22238388780"

    if method == 'fixed':
        if request.method == 'POST':
            form = VehiclePaymentProofForm(request.POST, request.FILES)
            if form.is_valid():
                screenshot = form.cleaned_data['screenshot']
                app_used = form.cleaned_data['app_used']

                # 1. حفظ معلومات الدفع في السيارة
                vehicle.payment_method = 'fixed'
                vehicle.save()

                # 2. حفظ أو تحديث إثبات الدفع
                VehiclePaymentProof.objects.update_or_create(
                    vehicle=vehicle,
                    defaults={
                        'app_used': app_used,
                        'screenshot': screenshot
                    }
                )

                messages.success(request, "✅ تم إرسال إثبات الدفع بنجاح.")
                return redirect('dashboard')
        else:
            form = VehiclePaymentProofForm()
    else:
        # إذا اختار المستخدم العمولة
        if request.method == 'POST':
            vehicle.payment_method = 'commission'
            vehicle.save()
            messages.success(request, "✅ تم تفعيل اتفاق العمولة.")
            return redirect('dashboard')
        form = None

    return render(request, 'vehicles/vehicle_payment_instructions.html', {
        'vehicle': vehicle,
        'method': method,
        'admin_phone': admin_phone,
        'form': form
    })
