from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def split(value, arg='\n'):
    """Split string by given separator"""
    if not value:
        return []
    return value.split(arg)

@register.filter
def get_rating_count(reviews, rating):
    """Count reviews with specific rating"""
    return reviews.filter(rating=rating).count()

@register.filter
def divide(value, arg):
    """Divide value by arg"""
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def multiply(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except ValueError:
        return 0

@register.filter
def to_list(value):
    """Convert value to list"""
    if isinstance(value, list):
        return value
    return list(value)