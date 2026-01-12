from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

class ScholarshipsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scholarships'
    verbose_name = _('Scholarships')