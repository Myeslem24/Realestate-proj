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

def home_view(request):
    city = request.GET.get('city')
    district = request.GET.get('district')

    properties = Property.objects.filter(status='approved')

    if city:
        properties = properties.filter(main_location=city)
    if district and city == 'نواكشوط':
        properties = properties.filter(district=district)

    # عرض فقط 4 عقارات
    properties = properties[:4]

    context = {
        'properties': properties,
        'year': datetime.now().year,
        'selected_city': city,
        'selected_district': district,
        'cities': Property.MAIN_LOCATIONS,
        'districts': Property.NAWAKCHOTT_DISTRICTS if city == 'نواكشوط' else [],
    }
    return render(request, 'home.html', context)
# عرض العقارات مع خاصية التصفية حسب المنطقة والحي
def property_list(request):
    properties = Property.objects.filter(status='approved')
    region = request.GET.get('region')
    neighborhood = request.GET.get('neighborhood')

    if region:
        properties = properties.filter(region__icontains=region)
    if neighborhood:
        properties = properties.filter(neighborhood__icontains=neighborhood)

    admin_phone = '22238388780'
    return render(request, 'properties/property_list.html', {
        'properties': properties,
        'admin_phone': admin_phone,
        'selected_region': region,
        'selected_neighborhood': neighborhood,
    })

# ✅ إصلاح بسيط في add_property (المسافة في السطر 35)
@login_required(login_url='/accounts/login/')
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST)
        media_formset = PropertyMediaFormSet(request.POST, request.FILES)

        if form.is_valid() and media_formset.is_valid():
            property = form.save(commit=False)
            property.owner = request.user
            property.save()

            for media in media_formset:
                if media.cleaned_data:
                    media_obj = media.save(commit=False)
                    media_obj.property = property
                    media_obj.save()

            messages.success(request, 'تم إرسال العقار للمراجعة.')
            return redirect('dashboard')
    else:
        form = PropertyForm()
        media_formset = PropertyMediaFormSet()

    return render(request, 'properties/add_property.html', {
        'form': form,
        'media_formset': media_formset,
    })

@staff_member_required
def review_properties(request):
    pending_properties = Property.objects.filter(status='pending')
    return render(request, 'admin/review_properties.html', {'properties': pending_properties})


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

    statuses = [
        ('all', 'الكل'),
        ('pending', 'قيد المراجعة'),
        ('approved', 'مقبول'),
        ('rejected', 'مرفوض'),
    ]

    return render(request, 'properties/dashboard.html', {
        'my_properties': my_properties,
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

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=property_obj)
        if form.is_valid():
            updated_property = form.save(commit=False)
            updated_property.status = 'pending'  # عند التعديل، يعود العقار لحالة "قيد المراجعة"
            updated_property.save()
            messages.success(request, "✅ تم تعديل العقار بنجاح. التعديلات قيد المراجعة.")
            return redirect('dashboard')  # تأكد أن اسم الـ URL هو dashboard
    else:
        form = PropertyForm(instance=property_obj)

    return render(request, 'properties/edit_property.html', {'form': form})

@login_required
def delete_property(request, property_id):
    property_obj = get_object_or_404(Property, id=property_id, owner=request.user)
    property_obj.delete()
    messages.success(request, "تم حذف العقار بنجاح.")
    return redirect('dashboard')
