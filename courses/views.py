from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Avg, Count
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from .models import Course, CourseModule, CourseLesson, Enrollment, Review
from .forms import CourseForm, ReviewForm

def course_list(request):
    """عرض قائمة الكورسات"""
    courses = Course.objects.filter(status='published').order_by('-created_at')
    
    # التصفية
    query = request.GET.get('q')
    level = request.GET.get('level')
    category = request.GET.get('category')
    sort = request.GET.get('sort', 'newest')
    
    if query:
        courses = courses.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(instructor__icontains=query)
        )
    
    if level:
        courses = courses.filter(level=level)
    
    if category:
        courses = courses.filter(categories__slug=category)
    
    # الترتيب
    if sort == 'popular':
        courses = courses.order_by('-enrollment_count')
    elif sort == 'rating':
        courses = courses.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    elif sort == 'price_low':
        courses = courses.order_by('price')
    elif sort == 'price_high':
        courses = courses.order_by('-price')
    else:  # newest
        courses = courses.order_by('-created_at')
    
    # الكورسات المميزة
    featured_courses = courses.filter(is_featured=True)[:3]
    
    # الإحصائيات
    total_courses = Course.objects.filter(status='published').count()
    total_enrollments = Enrollment.objects.count()
    total_instructors = Course.objects.filter(status='published').values('author').distinct().count()
    average_rating = Review.objects.aggregate(avg=Avg('rating'))['avg'] or 0
    
    # الترقيم
    paginator = Paginator(courses, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'courses': page_obj,
        'featured_courses': featured_courses,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'total_instructors': total_instructors,
        'average_rating': round(average_rating, 1),
        'query': query,
        'level': level,
        'category': category,
        'sort': sort,
    }
    
    return render(request, 'courses/list.html', context)

def course_detail(request, slug):
    """عرض تفاصيل الكورس"""
    course = get_object_or_404(Course, slug=slug, status='published')
    
    # زيادة عدد المشاهدات
    course.increment_views()
    
    # التحقق من تسجيل المستخدم
    user_enrolled = False
    user_review = None
    if request.user.is_authenticated:
        user_enrolled = Enrollment.objects.filter(
            user=request.user, 
            course=course
        ).exists()
        user_review = Review.objects.filter(
            user=request.user,
            course=course
        ).first()
    
    # الكورسات المشابهة
    related_courses = Course.objects.filter(
        categories__in=course.categories.all(),
        status='published'
    ).exclude(id=course.id).distinct()[:4]
    
    # المراجعات
    reviews = course.reviews.filter(is_approved=True).order_by('-created_at')
    
    # متوسط التقييم
    average_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    course.average_rating = round(average_rating, 1)
    
    # إحصائيات المدرب
    instructor_stats = {
        'total_courses': Course.objects.filter(
            author=course.author,
            status='published'
        ).count(),
        'total_students': Enrollment.objects.filter(
            course__author=course.author
        ).count(),
        'average_rating': Review.objects.filter(
            course__author=course.author
        ).aggregate(avg=Avg('rating'))['avg'] or 0,
        'total_reviews': Review.objects.filter(
            course__author=course.author
        ).count(),
    }
    
    context = {
        'course': course,
        'user_enrolled': user_enrolled,
        'user_review': user_review,
        'related_courses': related_courses,
        'reviews': reviews,
        'instructor_stats': instructor_stats,
        'total_reviews': reviews.count(),
    }
    
    return render(request, 'courses/detail.html', context)

@login_required
def enroll_course(request, course_id):
    """تسجيل الطالب في الكورس"""
    course = get_object_or_404(Course, id=course_id, status='published')
    
    # التحقق من عدم التسجيل مسبقًا
    if Enrollment.objects.filter(user=request.user, course=course).exists():
        return JsonResponse({
            'success': False,
            'error': _('You are already enrolled in this course')
        })
    
    # إنشاء التسجيل
    Enrollment.objects.create(user=request.user, course=course)
    
    # زيادة عدد المسجلين
    course.increment_enrollment()
    
    return JsonResponse({
        'success': True,
        'message': _('Successfully enrolled in the course!')
    })

@login_required
def add_review(request, slug):
    """إضافة تقييم للكورس"""
    course = get_object_or_404(Course, slug=slug, status='published')
    
    # التحقق من تسجيل المستخدم في الكورس
    if not Enrollment.objects.filter(user=request.user, course=course).exists():
        messages.error(request, _('You must enroll in the course first'))
        return redirect('courses:detail', slug=slug)
    
    # التحقق من عدم إضافة تقييم مسبقًا
    if Review.objects.filter(user=request.user, course=course).exists():
        messages.error(request, _('You have already reviewed this course'))
        return redirect('courses:detail', slug=slug)
    
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.course = course
            review.save()
            
            messages.success(request, _('Thank you for your review!'))
            return redirect('courses:detail', slug=slug)
    else:
        form = ReviewForm()
    
    return redirect('courses:detail', slug=slug)

@login_required
def learn_course(request, slug):
    """صفحة التعلم"""
    course = get_object_or_404(Course, slug=slug, status='published')
    
    # التحقق من تسجيل المستخدم
    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    if not enrollment:
        messages.error(request, _('You must enroll in the course first'))
        return redirect('courses:detail', slug=slug)
    
    # الحصول على الوحدات والدروس
    modules = course.modules.all().prefetch_related('lessons')
    
    # تتبع التقدم
    progress = 0
    total_lessons = sum(module.lessons.count() for module in modules)
    if total_lessons > 0:
        # في تطبيق حقيقي، يجب تتبع الدروس المكتملة
        completed_lessons = 0
        progress = int((completed_lessons / total_lessons) * 100)
    
    context = {
        'course': course,
        'modules': modules,
        'enrollment': enrollment,
        'progress': progress,
    }
    
    return render(request, 'courses/learn.html', context)

@login_required
def my_courses(request):
    """الكورسات المسجل فيها المستخدم"""
    enrollments = Enrollment.objects.filter(user=request.user).select_related('course')
    
    # التصنيف حسب الحالة
    active_courses = []
    completed_courses = []
    
    for enrollment in enrollments:
        if enrollment.completed:
            completed_courses.append(enrollment)
        else:
            active_courses.append(enrollment)
    
    context = {
        'active_courses': active_courses,
        'completed_courses': completed_courses,
    }
    
    return render(request, 'courses/my_courses.html', context)