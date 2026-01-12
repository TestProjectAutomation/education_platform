from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from django.db.models import Sum
from datetime import datetime, timedelta
from .models import Advertisement, AdPlacement
# from .forms import AdvertisementForm, AdPlacementForm

def record_impression(request, ad_id):
    """تسجيل ظهور الإعلان"""
    ad = get_object_or_404(Advertisement, id=ad_id)
    ad.record_impression()
    return JsonResponse({'success': True})

def record_click(request, ad_id):
    """تسجيل نقرة على الإعلان"""
    ad = get_object_or_404(Advertisement, id=ad_id)
    ad.record_click()
    return redirect(ad.link)

@login_required
@user_passes_test(lambda u: u.user_type in ['admin', 'editor'])
def ad_dashboard(request):
    """لوحة تحكم الإعلانات"""
    ads = Advertisement.objects.all().order_by('-start_date')
    
    # الإحصائيات
    total_ads = ads.count()
    active_ads = sum(1 for ad in ads if ad.is_active())
    total_impressions = ads.aggregate(Sum('impressions'))['impressions__sum'] or 0
    total_clicks = ads.aggregate(Sum('clicks'))['clicks__sum'] or 0
    
    # نسبة النقر
    ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
    
    # الإعلانات المنتهية قريبًا (خلال 7 أيام)
    warning_date = datetime.now().date() + timedelta(days=7)
    expiring_ads = ads.filter(end_date__lte=warning_date, end_date__gte=datetime.now().date())
    
    context = {
        'ads': ads[:10],  # آخر 10 إعلانات
        'total_ads': total_ads,
        'active_ads': active_ads,
        'total_impressions': total_impressions,
        'total_clicks': total_clicks,
        'ctr': round(ctr, 2),
        'expiring_ads': expiring_ads,
    }
    
    return render(request, 'advertisements/dashboard.html', context)

@login_required
@user_passes_test(lambda u: u.user_type in ['admin', 'editor'])
def create_ad(request):
    """إنشاء إعلان جديد"""
    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES)
        if form.is_valid():
            ad = form.save(commit=False)
            ad.save()
            messages.success(request, _('Advertisement created successfully'))
            return redirect('advertisements:dashboard')
    else:
        form = AdvertisementForm()
    
    context = {
        'form': form,
        'title': _('Create New Advertisement'),
    }
    
    return render(request, 'advertisements/form.html', context)

@login_required
@user_passes_test(lambda u: u.user_type in ['admin', 'editor'])
def edit_ad(request, pk):
    """تعديل الإعلان"""
    ad = get_object_or_404(Advertisement, pk=pk)
    
    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES, instance=ad)
        if form.is_valid():
            form.save()
            messages.success(request, _('Advertisement updated successfully'))
            return redirect('advertisements:dashboard')
    else:
        form = AdvertisementForm(instance=ad)
    
    context = {
        'form': form,
        'title': _('Edit Advertisement'),
        'ad': ad,
    }
    
    return render(request, 'advertisements/form.html', context)

@login_required
@user_passes_test(lambda u: u.user_type == 'admin')
def manage_placements(request):
    """إدارة أماكن الإعلانات"""
    placements = AdPlacement.objects.all()
    
    if request.method == 'POST':
        form = AdPlacementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, _('Ad placement created successfully'))
            return redirect('advertisements:placements')
    else:
        form = AdPlacementForm()
    
    context = {
        'placements': placements,
        'form': form,
    }
    
    return render(request, 'advertisements/placements.html', context)

@login_required
@user_passes_test(lambda u: u.user_type == 'admin')
def toggle_ad_status(request, pk):
    """تفعيل/تعطيل الإعلان"""
    ad = get_object_or_404(Advertisement, pk=pk)
    ad.active = not ad.active
    ad.save()
    
    status = _('activated') if ad.active else _('deactivated')
    messages.success(request, f'Advertisement {status} successfully')
    
    return redirect('advertisements:dashboard')

@login_required
@user_passes_test(lambda u: u.user_type == 'admin')
def delete_ad(request, pk):
    """حذف الإعلان"""
    ad = get_object_or_404(Advertisement, pk=pk)
    ad.delete()
    
    messages.success(request, _('Advertisement deleted successfully'))
    return redirect('advertisements:dashboard')