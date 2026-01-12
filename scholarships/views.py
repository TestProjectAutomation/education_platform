from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import Scholarship

def scholarship_list(request):
    """عرض قائمة المنح"""
    scholarships = Scholarship.objects.filter(status='published').order_by('-created_at')
    
    # التصفية
    query = request.GET.get('q')
    country = request.GET.get('country')
    scholarship_type = request.GET.get('type')
    category = request.GET.get('category')
    
    if query:
        scholarships = scholarships.filter(
            Q(title__icontains=query) |
            Q(university__icontains=query) |
            Q(content__icontains=query)
        )
    
    if country:
        scholarships = scholarships.filter(country__icontains=country)
    
    if scholarship_type:
        scholarships = scholarships.filter(scholarship_type=scholarship_type)
    
    if category:
        scholarships = scholarships.filter(categories__slug=category)
    
    # المنح المميزة
    featured_scholarships = scholarships.filter(is_featured=True)[:4]
    
    # المنح المنتهية والجارية
    active_scholarships = scholarships.filter(deadline__gte=timezone.now().date())
    expired_scholarships = scholarships.filter(deadline__lt=timezone.now().date())
    
    # البلدان المتاحة
    countries = scholarships.values_list('country', flat=True).distinct()
    
    # الترقيم
    paginator = Paginator(scholarships, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'scholarships': page_obj,
        'featured_scholarships': featured_scholarships,
        'active_scholarships': active_scholarships,
        'expired_scholarships': expired_scholarships,
        'countries': countries,
        'query': query,
        'country': country,
        'scholarship_type': scholarship_type,
        'category': category,
    }
    
    return render(request, 'scholarships/list.html', context)

def scholarship_detail(request, slug):
    """عرض تفاصيل المنحة"""
    scholarship = get_object_or_404(Scholarship, slug=slug, status='published')
    
    # زيادة عدد المشاهدات
    scholarship.increment_views()
    
    # المنح المشابهة
    related_scholarships = Scholarship.objects.filter(
        country=scholarship.country,
        status='published'
    ).exclude(id=scholarship.id)[:3]
    
    # نصائح التقديم
    application_tips = scholarship.tips.all()
    
    context = {
        'scholarship': scholarship,
        'related_scholarships': related_scholarships,
        'application_tips': application_tips,
    }
    
    return render(request, 'scholarships/detail.html', context)

def scholarship_country(request, country):
    """عرض المنح حسب البلد"""
    scholarships = Scholarship.objects.filter(
        country__icontains=country,
        status='published'
    ).order_by('-created_at')
    
    # الترقيم
    paginator = Paginator(scholarships, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'country': country,
        'scholarships': page_obj,
    }
    
    return render(request, 'scholarships/country.html', context)