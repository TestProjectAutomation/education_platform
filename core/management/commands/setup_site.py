from django.core.management.base import BaseCommand
from django.utils.translation import gettext_lazy as _
from core.models import SiteSetting, Category

class Command(BaseCommand):
    help = 'Initialize the site with default settings and categories'
    
    def handle(self, *args, **options):
        # إنشاء إعدادات الموقع
        site_settings, created = SiteSetting.objects.get_or_create(
            pk=1,
            defaults={
                'site_name': 'منصة التعليم',
                'site_description': 'منصة تعليمية متكاملة تقدم كورسات ومقالات وكتب ومنح دراسية',
                'default_language': 'ar',
                'contact_email': 'info@eduplatform.com'
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('Site settings created successfully'))
        else:
            self.stdout.write('Site settings already exist')
        
        # إنشاء التصنيفات الأساسية
        categories = [
            {'name': 'تطوير الويب', 'slug': 'web-development', 'order': 1},
            {'name': 'تطوير تطبيقات الموبايل', 'slug': 'mobile-development', 'order': 2},
            {'name': 'علوم البيانات', 'slug': 'data-science', 'order': 3},
            {'name': 'التسويق الرقمي', 'slug': 'digital-marketing', 'order': 4},
            {'name': 'اللغة الإنجليزية', 'slug': 'english-language', 'order': 5},
            {'name': 'التصميم الجرافيكي', 'slug': 'graphic-design', 'order': 6},
            {'name': 'إدارة الأعمال', 'slug': 'business-management', 'order': 7},
            {'name': 'الصحة واللياقة', 'slug': 'health-fitness', 'order': 8},
        ]
        
        created_count = 0
        for cat_data in categories:
            category, created = Category.objects.get_or_create(
                slug=cat_data['slug'],
                defaults={
                    'name': cat_data['name'],
                    'order': cat_data['order']
                }
            )
            if created:
                created_count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {created_count} categories'))