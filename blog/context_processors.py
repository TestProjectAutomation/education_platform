from blog.models import Category


def categories_processor(request):
    """
    Makes all categories available in all templates.
    """
    categories = Category.objects.filter(is_active=True).order_by('order', 'name_ar')
    return {
        'all_categories': categories
    }
