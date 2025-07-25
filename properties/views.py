from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.forms import modelformset_factory
from django.urls import reverse
from django.conf import settings

from .models import Property, PropertyMedia, PaymentProof, CustomUser
from .forms import (
    PropertyForm,
    PropertyMediaFormSet,
    PaymentProofForm,
    LoginForm,
    CustomUserCreationForm,
    PropertyMediaForm,
)
from vehicles.models import Vehicle, CarBrand, CarModel

import os
from datetime import datetime


def home_view(request):
    city = request.GET.get('city')
    district = request.GET.get('district')
    purpose = request.GET.get('purpose')
    brand_id = request.GET.get('brand')
    model_id = request.GET.get('model')
    year = request.GET.get('year')
    filter_type = request.GET.get('filter_type')

    properties = Property.objects.filter(status='approved')
    vehicles = Vehicle.objects.filter(status='approved')

    if filter_type == 'property':
        if city:
            properties = properties.filter(main_location=city)
        if district and city == 'نواكشوط':
            properties = properties.filter(district=district)
        if purpose:
            properties = properties.filter(purpose=purpose)
        vehicles = Vehicle.objects.none()

    elif filter_type == 'vehicle':
        if brand_id:
            vehicles = vehicles.filter(brand_id=brand_id)
        if model_id:
            vehicles = vehicles.filter(model_id=model_id)
        if year:
            vehicles = vehicles.filter(year=year)
        properties = Property.objects.none()

    context = {
        'properties': properties[:4],
        'vehicles': vehicles[:4],
        'selected_city': city,
        'selected_district': district,
        'selected_purpose': purpose,
        'selected_brand': brand_id,
        'selected_model': model_id,
        'selected_year': year,
        'filter_type': filter_type,
        'cities': Property.MAIN_LOCATIONS,
        'districts': Property.NAWAKCHOTT_DISTRICTS if city == 'نواكشوط' else [],
        'purposes': Property.PURPOSE_CHOICES,
        'brands': CarBrand.objects.all(),
        'models': CarModel.objects.filter(brand_id=brand_id) if brand_id else CarModel.objects.none(),
        'year': datetime.now().year,
    }

    return render(request, 'home.html', context)


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


@login_required
def add_property(request):
    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES)
        media_formset = PropertyMediaFormSet(request.POST, request.FILES, queryset=PropertyMedia.objects.none())

        if form.is_valid() and media_formset.is_valid():
            prop = form.save(commit=False)
            prop.owner = request.user
            prop.save()

            images_count = 0
            for media in media_formset:
                if media.cleaned_data.get('image'):
                    media_obj = media.save(commit=False)
                    media_obj.property = prop
                    media_obj.save()
                    images_count += 1

            if images_count < 3:
                messages.warning(request, '📸 يُفضّل رفع 3 صور إضافية لتحسين عرض العقار.')

            return redirect('choose_payment_option', property_id=prop.id)

        messages.error(request, '⚠️ يرجى تصحيح الأخطاء أدناه.')
    else:
        form = PropertyForm()
        media_formset = PropertyMediaFormSet(queryset=PropertyMedia.objects.none())

    return render(request, 'properties/add_property.html', {
        'form': form,
        'media_formset': media_formset,
    })


@login_required
def edit_property(request, property_id):
    prop = get_object_or_404(Property, id=property_id, owner=request.user)

    PropertyMediaFormSetEditable = modelformset_factory(
        PropertyMedia,
        form=PropertyMediaForm,
        fields=['image'],
        extra=3,
        can_delete=True
    )

    if request.method == 'POST':
        form = PropertyForm(request.POST, request.FILES, instance=prop)
        media_formset = PropertyMediaFormSetEditable(
            request.POST, request.FILES,
            queryset=PropertyMedia.objects.filter(property=prop)
        )

        if form.is_valid() and media_formset.is_valid():
            prop = form.save(commit=False)
            prop.status = 'pending'
            prop.save()
            media_formset.save()

            total_images = PropertyMedia.objects.filter(property=prop).count()
            if total_images < 3:
                messages.warning(request, '📸 يُفضل أن يكون لديك 3 صور إضافية على الأقل.')

            messages.success(request, '✅ تم تعديل العقار بنجاح. التعديلات قيد المراجعة.')
            return redirect('dashboard')

        messages.error(request, '⚠️ يرجى تصحيح الأخطاء أدناه.')
    else:
        form = PropertyForm(instance=prop)
        media_formset = PropertyMediaFormSetEditable(queryset=PropertyMedia.objects.filter(property=prop))

    return render(request, 'properties/edit_property.html', {
        'form': form,
        'media_formset': media_formset,
        'property': prop,
    })


@login_required
def delete_property(request, property_id):
    prop = get_object_or_404(Property, id=property_id, owner=request.user)
    prop.delete()
    messages.success(request, "تم حذف العقار بنجاح.")
    return redirect('dashboard')


@staff_member_required
def review_properties(request):
    pending_properties = Property.objects.filter(status='pending')
    return render(request, 'properties/review_properties.html', {'properties': pending_properties})


@staff_member_required
def approve_property(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    prop.status = 'approved'
    prop.save()
    messages.success(request, 'تم قبول العقار بنجاح.')
    return redirect('review_properties')


@staff_member_required
def reject_property(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    prop.status = 'rejected'
    prop.save()
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


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_approved = True
            user.save()
            user.backend = 'properties.backends.PhoneEmailBackend'
            login(request, user)
            return redirect('dashboard')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


def login_view(request):
    form = LoginForm(request.POST or None)
    error_message = None

    if request.method == 'POST':
        identifier = form.data.get('identifier')
        password = form.data.get('password')

        user = None
        try:
            user = CustomUser.objects.get(phone_number=identifier)
        except CustomUser.DoesNotExist:
            try:
                user = CustomUser.objects.get(email=identifier)
            except CustomUser.DoesNotExist:
                pass

        if user:
            user_auth = authenticate(request, phone_number=user.phone_number, password=password)
            if user_auth:
                login(request, user_auth)
                next_url = request.GET.get('next') or reverse('dashboard')
                return redirect(next_url)
            else:
                error_message = "كلمة المرور غير صحيحة"
        else:
            error_message = "رقم الهاتف أو البريد الإلكتروني غير صحيح"

    return render(request, 'registration/login.html', {'form': form, 'error': error_message})


def property_detail(request, pk):
    prop = get_object_or_404(Property, pk=pk)
    return render(request, 'properties/detail.html', {'property': prop})


def we_are_view(request):
    return render(request, 'properties/we_are.html')

@login_required
def choose_payment_option(request, property_id):
    property_instance = get_object_or_404(Property, id=property_id, owner=request.user)

    if request.method == "POST":
        option = request.POST.get("payment_option")
        if option == "fixed":
            return redirect('payment_instructions', property_id=property_id, method='fixed')
        elif option == "commission":
            return redirect('payment_instructions', property_id=property_id, method='commission')

    return render(request, 'properties/payment_option.html', {'property': property_instance})

@login_required
def payment_instructions(request, property_id, method):
    prop = get_object_or_404(Property, id=property_id, owner=request.user)
    admin_phone = "22238388780"

    if method == 'fixed':
        if request.method == 'POST':
            form = PaymentProofForm(request.POST, request.FILES)
            if form.is_valid():
                screenshot = form.cleaned_data['screenshot']
                app_used = form.cleaned_data['app_used']

                prop.payment_method = 'fixed'
                prop.app_used = app_used
                prop.save()

                PaymentProof.objects.update_or_create(
                    property=prop,
                    defaults={'app_used': app_used, 'screenshot': screenshot}
                )

                messages.success(request, "✅ تم إرسال إثبات الدفع بنجاح.")
                return redirect('dashboard')
        else:
            form = PaymentProofForm()
    else:
        if request.method == 'POST':
            prop.payment_method = 'commission'
            prop.save()
            return redirect('dashboard')
        form = None

    return render(request, 'properties/payment_instructions.html', {
        'property': prop,
        'method': method,
        'admin_phone': admin_phone,
        'form': form
    })


def get_districts(request):
    city = request.GET.get("city")
    if city == "نواكشوط":
        return JsonResponse([
            {"value": value, "label": label}
            for value, label in Property.NAWAKCHOTT_DISTRICTS
        ], safe=False)
    return JsonResponse([], safe=False)
