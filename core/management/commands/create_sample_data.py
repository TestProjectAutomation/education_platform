from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from core.models import Category
from courses.models import Course
from articles.models import Article, Tag
from books.models import Book
from scholarships.models import Scholarship
from faker import Faker
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create sample data for development'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Number of items to create for each model'
        )
    
    def handle(self, *args, **options):
        fake = Faker()
        count = options['count']
        
        self.stdout.write(self.style.SUCCESS('Creating sample data...'))
        
        # إنشاء مستخدمين
        self.stdout.write('Creating users...')
        users = []
        for i in range(5):
            user = User.objects.create_user(
                username=fake.user_name(),
                email=fake.email(),
                password='password123',
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                user_type=random.choice(['user', 'editor', 'admin'])
            )
            users.append(user)
        
        # إنشاء تصنيفات
        self.stdout.write('Creating categories...')
        categories = []
        for cat_name in [
            'Programming', 'Design', 'Business', 'Science',
            'Languages', 'Health', 'Arts', 'Technology'
        ]:
            category, created = Category.objects.get_or_create(
                name=cat_name,
                defaults={'slug': cat_name.lower().replace(' ', '-')}
            )
            categories.append(category)
        
        # إنشاء وسوم
        self.stdout.write('Creating tags...')
        tags = []
        for tag_name in [
            'Python', 'JavaScript', 'Web Development', 'Mobile',
            'Data Science', 'Machine Learning', 'UI/UX', 'Marketing'
        ]:
            tag, created = Tag.objects.get_or_create(
                name=tag_name,
                defaults={'slug': tag_name.lower().replace(' ', '-')}
            )
            tags.append(tag)
        
        # إنشاء كورسات
        self.stdout.write('Creating courses...')
        for i in range(count):
            course = Course.objects.create(
                title=fake.sentence(),
                slug=f'sample-course-{i}',
                content=fake.text(2000),
                excerpt=fake.text(200),
                price=random.choice([0, 99, 199, 299]),
                discount_price=random.choice([None, 79, 149, 249]),
                duration=f'{random.randint(4, 12)} weeks',
                level=random.choice(['beginner', 'intermediate', 'advanced']),
                instructor=fake.name(),
                requirements=fake.text(300),
                what_you_will_learn=fake.text(500),
                author=random.choice(users),
                status=random.choice(['draft', 'published']),
                is_featured=random.choice([True, False]),
                link_display_duration=30
            )
            course.categories.set(random.sample(categories, 3))
        
        # إنشاء مقالات
        self.stdout.write('Creating articles...')
        for i in range(count):
            article = Article.objects.create(
                title=fake.sentence(),
                slug=f'sample-article-{i}',
                content=fake.text(1500),
                excerpt=fake.text(150),
                reading_time=random.randint(3, 15),
                author=random.choice(users),
                status=random.choice(['draft', 'published']),
                is_featured=random.choice([True, False]),
                link_display_duration=30
            )
            article.categories.set(random.sample(categories, 2))
            article.tags.set(random.sample(tags, 3))
        
        # إنشاء كتب
        self.stdout.write('Creating books...')
        for i in range(count):
            book = Book.objects.create(
                title=fake.sentence(),
                slug=f'sample-book-{i}',
                content=fake.text(1000),
                excerpt=fake.text(150),
                book_type=random.choice(['book', 'summary', 'notes']),
                author=fake.name(),
                publisher=fake.company(),
                publication_year=random.randint(2000, 2023),
                pages=random.randint(100, 500),
                isbn=fake.isbn13(),
                download_link=fake.url(),
                author=random.choice(users),
                status=random.choice(['draft', 'published']),
                is_featured=random.choice([True, False]),
                link_display_duration=30
            )
            book.categories.set(random.sample(categories, 2))
        
        # إنشاء منح
        self.stdout.write('Creating scholarships...')
        for i in range(count):
            scholarship = Scholarship.objects.create(
                title=fake.sentence(),
                slug=f'sample-scholarship-{i}',
                content=fake.text(1200),
                excerpt=fake.text(150),
                scholarship_type=random.choice(['undergraduate', 'masters', 'phd']),
                country=fake.country(),
                university=fake.company(),
                deadline=fake.future_date(),
                funding_amount=fake.text(100),
                eligibility=fake.text(300),
                application_process=fake.text(300),
                official_link=fake.url(),
                author=random.choice(users),
                status=random.choice(['draft', 'published']),
                is_featured=random.choice([True, False]),
                link_display_duration=30
            )
            scholarship.categories.set(random.sample(categories, 2))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} items for each model'))