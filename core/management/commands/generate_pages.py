from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from pages.models import Page
import random
from django.utils import timezone

class Command(BaseCommand):
    help = 'Generate sample pages for testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=50,
            help='Number of pages to generate'
        )
    
    def handle(self, *args, **options):
        count = options['count']
        
        # Get or create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
        
        # Sample data
        titles = [
            'About Us', 'Contact', 'Services', 'Products', 'Blog',
            'FAQ', 'Terms of Service', 'Privacy Policy', 'Team',
            'Careers', 'Portfolio', 'Testimonials', 'Pricing',
            'Documentation', 'Support', 'Tutorials', 'Resources',
            'Events', 'News', 'Gallery', 'Downloads', 'Forum',
            'Shop', 'Members', 'Dashboard', 'Settings', 'Profile'
        ]
        
        templates = ['default', 'fullwidth', 'sidebar_left', 'sidebar_right']
        statuses = ['draft', 'published', 'private']
        
        for i in range(count):
            title = random.choice(titles) + f' {i+1}'
            slug = f'{title.lower().replace(" ", "-")}-{i+1}'
            
            page = Page.objects.create(
                title=title,
                slug=slug,
                content=f'<h1>{title}</h1><p>This is sample content for {title}.</p>',
                excerpt=f'Sample excerpt for {title}',
                template=random.choice(templates),
                status=random.choice(statuses),
                order=i,
                show_in_menu=random.choice([True, False]),
                author=admin_user,
                views=random.randint(0, 1000),
                allow_comments=random.choice([True, False])
            )
            
            # Random parent assignment
            if i > 0 and random.choice([True, False]):
                parent = Page.objects.order_by('?').first()
                page.parent = parent
                page.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Created page: {title}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully generated {count} pages')
        )