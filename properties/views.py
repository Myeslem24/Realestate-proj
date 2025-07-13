# properties/views.py
from django.db.models import Q  # أضف هذا في الأعلى
from django.shortcuts import render, redirect
from .models import Property, PropertyMedia
from .forms import PropertyForm, PropertyMediaFormSet
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from datetime import datetime
from django.contrib.auth.forms import UserCreationForm
from .forms import CustomUserCreationForm
from django.contrib.auth import login
from vehicles.models import Vehicle  # تأكد من الاستيراد
from vehicles.models import Vehicle, CarBrand, CarModel  # ✅ استيراد بيانات السيا
from django.http import JsonResponse
from .forms import PaymentProofForm
import os  # ✅ هذا السطر المهم
from django.conf import settings  # ✅ مهم
from .models import PaymentProof

def home_view(request):
    # طلبات GET
    city = request.GET.get('city')
    district = request.GET.get('district')
    purpose = request.GET.get('purpose')
    brand_id = request.GET.get('brand')
    model_id = request.GET.get('model')
    year = request.GET.get('year')
    filter_type = request.GET.get('filter_type')

    # استعلامات مبدئية
    properties = Property.objects.filter(status='approved')
    vehicles = Vehicle.objects.filter(status='approved')

    # تصفية حسب نوع العرض
    if filter_type == 'property':
        if city:
            properties = properties.filter(main_location=city)
        if district and city == 'نواكشوط':
            properties = properties.filter(district=district)
        if purpose:
            properties = properties.filter(purpose=purpose)
        vehicles = Vehicle.objects.none()  # إخفاء السيارات

    elif filter_type == 'vehicle':
        if brand_id:
            vehicles = vehicles.filter(brand_id=brand_id)
        if model_id:
            vehicles = vehicles.filter(model_id=model_id)
        if year:
            vehicles = vehicles.filter(year=year)
        properties = Property.objects.none()  # إخفاء العقارات

    # بيانات الإرسال إلى القالب
    context = {
        'properties': properties[:4],   # عرض 4 فقط
        'vehicles': vehicles[:4],       # عرض 4 فقط
        'selected_city': city,
        'selected_district': district,
        'selected_purpose': purpose,
        'selected_brand': brand_id,
        'selected_model': model_id,
        'selected_year': year,
        'filter_type': filter_type,

        # القوائم
        'cities': Property.MAIN_LOCATIONS,
        'districts': Property.NAWAKCHOTT_DISTRICTS if city == 'نواكشوط' else [],
        'purposes': Property.PURPOSE_CHOICES,
        'brands': CarBrand.objects.all(),
        'models': CarModel.objects.filter(brand_id=brand_id) if brand_id else CarModel.objects.none(),
        'year': datetime.now().year,
    }

    return render(request, 'home.html', context)

# عرض العقارات مع خاصية التصفية حسب المنطقة والحي
def property_list(request):
    city = request.GET.get('city')
    district = request.GET.get('district')
    purpose = request.GET.get('purpose')

    properties = Property.objects.filter(status='approved')

    if city:
        properties = properties.filter(main_location=city)
    if district and city == 'نواكشوط':
        properties = properties.filter(district=district)
    if purpose:
        properties = properties.filter(purpose=purpose)

    context = {
        'properties': properties,
        'admin_phone': '22238388780',
        'selected_city': city,
        'selected_district': district,
        'selected_purpose': purpose,
        'cities': Property.MAIN_LOCATIONS,
        'districts': Property.NAWAKCHOTT_DISTRICTS if city == 'نواكشوط' else [],
        'purposes': Property.PURPOSE_CHOICES,
    }

    return render(request, 'properties/property_list.html', context)
@login_required(login_url='/accounts/login/')
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        media_formset = PropertyMediaFormSet(request.POST, request.FILES, queryset=PropertyMedia.objects.none())

        if form.is_valid() and media_formset.is_valid():
            property = form.save(commit=False)
            property.owner = request.user
            property.save()

            images_count = 0
            for media in media_formset:
                if media.cleaned_data.get('image'):
                    media_obj = media.save(commit=False)
                    media_obj.property = property
                    media_obj.save()
                    images_count += 1

            if images_count < 3:
                messages.warning(request, '📸 يُفضّل رفع 3 صور إضافية لتحسين عرض العقار.')

            messages.success(request, '✅ تم إرسال العقار للمراجعة.')

            # ✅ إعادة التوجيه إلى صفحة اختيار الدفع
            return redirect('choose_payment_option', property_id=property.id)

        else:
            messages.error(request, '⚠️ يرجى تصحيح الأخطاء أدناه.')

    else:
        form = PropertyForm()
        media_formset = PropertyMediaFormSet(queryset=PropertyMedia.objects.none())

    return render(request, 'properties/add_property.html', {
        'form': form,
        'media_formset': media_formset,
    })
@staff_member_required
def review_properties(request):
    pending_properties = Property.objects.filter(status='pending')
    return render(request, 'properties/review_properties.html', {'properties': pending_properties})

@staff_member_required
def approve_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    property.status = 'approved'
    property.save()
    messages.success(request, 'تم قبول العقار بنجاح.')
    return redirect('review_properties')

@staff_member_required
def reject_property(request, pk):
    property = get_object_or_404(Property, pk=pk)
    property.status = 'rejected'
    property.save()
    messages.error(request, 'تم رفض العقار.')
    return redirect('review_properties')

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

    return render(request, 'properties/dashboard.html', {
        'my_properties': my_properties,
        'my_vehicles': my_vehicles,
        'statuses': statuses,
    })


# تعديل التسجيل ليكون المستخدم معتمد تلقائيًا
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_approved = True  # ✅ الموافقة التلقائية
            user.save()
            user.backend = 'properties.backends.PhoneEmailBackend'
            login(request, user)
            return redirect('dashboard')  # ✅ توجيه المستخدم إلى لوحة التحكم
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_view(request):
    form = LoginForm(request.POST or None)
    error_message = None

    if request.method == 'POST':
        identifier = form.data.get('identifier')
        password = form.data.get('password')

        try:
            user = CustomUser.objects.get(phone_number=identifier)
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(email=identifier)
            except CustomUser.DoesNotExist:
                user = None

        if user is not None:
            user_auth = authenticate(request, phone_number=user.phone_number, password=password)
            if user_auth is not None:
                login(request, user_auth)

                # ✅ إعادة التوجيه إلى الصفحة السابقة بعد تسجيل الدخول
                next_url = request.GET.get('next') or reverse('dashboard')
                return redirect(next_url)
            else:
                error_message = "كلمة المرور غير صحيحة"
        else:
            error_message = "رقم الهاتف أو البريد الإلكتروني غير صحيح"

    return render(request, 'registration/login.html', {'form': form, 'error': error_message})

def property_detail(request, pk):
    property = get_object_or_404(Property, pk=pk)
    return render(request, 'properties/detail.html', {'property': property})

def we_are_view(request):
    return render(request, 'properties/we_are.html')

@login_required
def edit_property(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id, owner=request.user)

    PropertyMediaFormSetEditable = modelformset_factory(
        PropertyMedia,
        form=PropertyMediaForm,
        fields=['image'],
        extra=3,
        can_delete=True
    )

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        media_formset = PropertyMediaFormSetEditable(
            request.POST, request.FILES,
            queryset=PropertyMedia.objects.filter(property=property_obj)
        )

        if form.is_valid() and media_formset.is_valid():
            property = form.save(commit=False)
            property.status = 'pending'  # يعود لحالة "قيد المراجعة"
            property.save()

            media_formset.save()

            total_images = PropertyMedia.objects.filter(property=property).count()
            if total_images < 3:
                messages.warning(request, '📸 يُفضل أن يكون لديك 3 صور إضافية على الأقل.')

            messages.success(request, '✅ تم تعديل العقار بنجاح. التعديلات قيد المراجعة.')
            return redirect('dashboard')
        else:
            messages.error(request, '⚠️ يرجى تصحيح الأخطاء أدناه.')
    else:
        form = PropertyForm(instance=property_obj)
        media_formset = PropertyMediaFormSetEditable(queryset=PropertyMedia.objects.filter(property=property_obj))

    return render(request, 'properties/edit_property.html', {
        'form': form,
        'media_formset': media_formset,
        'property': property_obj
    })
@login_required
def delete_property(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id, owner=request.user)
    property_obj.delete()
    messages.success(request, "تم حذف العقار بنجاح.")
    return redirect('dashboard')

def get_districts(request):
    city = request.GET.get("city")
    if city == "نواكشوط":
        return JsonResponse([
            {"value": value, "label": label}
            for value, label in Property.NAWAKCHOTT_DISTRICTS
        ], safe=False)
    return JsonResponse([], safe=False)
@login_required
def choose_payment_option(request, property_id):
    property = get_object_or_404(Property, id=property_id, owner=request.user)
    
    if request.method == "POST":
        option = request.POST.get("payment_option")
        if option in ['fixed', 'commission']:
            property.payment_method = option
            property.save()
            return redirect('payment_instructions', property_id=property_id, method=option)

    return render(request, 'properties/payment_option.html', {'property': property})

@login_required
def payment_instructions(request, property_id, method):
    property_instance = get_object_or_404(Property, id=property_id, owner=request.user)
    admin_phone = "22238388780"

    if method == 'fixed':
        if request.method == 'POST':
            form = PaymentProofForm(request.POST, request.FILES)
            if form.is_valid():
                screenshot = form.cleaned_data['screenshot']
                app_used = form.cleaned_data['app_used']

                # 1. حفظ طريقة الدفع والتطبيق في العقار
                property_instance.payment_method = 'fixed'
                property_instance.app_used = app_used
                property_instance.save()

                # 2. إنشاء أو تحديث إثبات الدفع في قاعدة البيانات
                PaymentProof.objects.update_or_create(
                    property=property_instance,
                    defaults={
                        'app_used': app_used,
                        'screenshot': screenshot,
                    }
                )

                messages.success(request, "✅ تم إرسال إثبات الدفع بنجاح.")
                return redirect('dashboard')
        else:
            form = PaymentProofForm()
    else:
        if request.method == 'POST':
            property_instance.payment_method = 'commission'
            property_instance.save()
            return redirect('dashboard')
        form = None

    return render(request, 'properties/payment_instructions.html', {
        'property': property_instance,
        'method': method,
        'admin_phone': admin_phone,
        'form': form
    })
