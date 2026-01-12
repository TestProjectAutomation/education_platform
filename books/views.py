from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import HttpResponse
from .models import Book, BookReview, DownloadHistory
# from .forms import BookReviewForm

def book_list(request):
    """عرض قائمة الكتب"""
    books = Book.objects.filter(status='published').order_by('-created_at')
    
    # التصفية
    query = request.GET.get('q')
    book_type = request.GET.get('type')
    category = request.GET.get('category')
    
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(content__icontains=query)
        )
    
    if book_type:
        books = books.filter(book_type=book_type)
    
    if category:
        books = books.filter(categories__slug=category)
    
    # الكتب المميزة
    featured_books = books.filter(is_featured=True)[:4]
    
    # الإحصائيات
    stats = {
        'total_books': Book.objects.filter(status='published', book_type='book').count(),
        'total_summaries': Book.objects.filter(status='published', book_type='summary').count(),
        'total_notes': Book.objects.filter(status='published', book_type='notes').count(),
    }
    
    # الترقيم
    paginator = Paginator(books, 16)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'books': page_obj,
        'featured_books': featured_books,
        'stats': stats,
        'query': query,
        'book_type': book_type,
        'category': category,
    }
    
    return render(request, 'books/list.html', context)

def book_detail(request, slug):
    """عرض تفاصيل الكتاب"""
    book = get_object_or_404(Book, slug=slug, status='published')
    
    # زيادة عدد المشاهدات
    book.increment_views()
    
    # الكتب المشابهة
    related_books = Book.objects.filter(
        categories__in=book.categories.all(),
        status='published'
    ).exclude(id=book.id).distinct()[:4]
    
    # التقييمات
    reviews = book.reviews.filter(is_approved=True).order_by('-created_at')
    
    # إضافة تقييم
    if request.method == 'POST':
        form = BookReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.save()
            
            messages.success(request, _('Thank you for your review! It will be published after moderation'))
            return redirect('books:detail', slug=slug)
    else:
        form = BookReviewForm()
    
    context = {
        'book': book,
        'related_books': related_books,
        'reviews': reviews,
        'form': form,
    }
    
    return render(request, 'books/detail.html', context)

def download_book(request, slug):
    """تحميل الكتاب"""
    book = get_object_or_404(Book, slug=slug, status='published')
    
    # تسجيل عملية التحميل
    DownloadHistory.objects.create(
        book=book,
        user=request.user if request.user.is_authenticated else None,
        ip_address=request.META.get('REMOTE_ADDR'),
        user_agent=request.META.get('HTTP_USER_AGENT', '')
    )
    
    # إذا كان الملف موجودًا
    if book.file:
        response = HttpResponse(book.file.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{book.title}.{book.file_type.lower()}"'
        return response
    elif book.download_link:
        return redirect(book.download_link)
    else:
        messages.error(request, _('No download available for this book'))
        return redirect('books:detail', slug=slug)

def preview_book(request, slug):
    """معاينة الكتاب"""
    book = get_object_or_404(Book, slug=slug, status='published')
    
    # هنا يمكن إضافة منطق لعرض صفحات معاينة
    context = {
        'book': book,
    }
    
    return render(request, 'books/preview.html', context)