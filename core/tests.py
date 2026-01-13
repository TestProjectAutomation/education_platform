from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Page, PageComment, PageRating
from django.utils import timezone

class PageModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.page = Page.objects.create(
            title='Test Page',
            slug='test-page',
            content='Test content',
            excerpt='Test excerpt',
            status='published',
            author=self.user
        )
    
    def test_page_creation(self):
        self.assertEqual(self.page.title, 'Test Page')
        self.assertEqual(self.page.status, 'published')
        self.assertTrue(self.page.is_published())
    
    def test_page_breadcrumbs(self):
        child_page = Page.objects.create(
            title='Child Page',
            slug='child-page',
            content='Child content',
            parent=self.page,
            status='published'
        )
        
        breadcrumbs = child_page.get_breadcrumbs()
        self.assertEqual(len(breadcrumbs), 3)  # Home + parent + child
        self.assertEqual(breadcrumbs[-1]['title'], 'Child Page')
    
    def test_page_views_increment(self):
        initial_views = self.page.views
        self.page.increment_views()
        self.page.refresh_from_db()
        self.assertEqual(self.page.views, initial_views + 1)

class PageViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.page = Page.objects.create(
            title='Test Page',
            slug='test-page',
            content='Test content',
            status='published'
        )
    
    def test_page_detail_view(self):
        response = self.client.get(reverse('pages:detail', args=['test-page']))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Page')
    
    def test_private_page_access(self):
        private_page = Page.objects.create(
            title='Private Page',
            slug='private-page',
            content='Private content',
            status='private'
        )
        
        # Anonymous user should get 404
        response = self.client.get(reverse('pages:detail', args=['private-page']))
        self.assertEqual(response.status_code, 404)
        
        # Authenticated user should access
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('pages:detail', args=['private-page']))
        self.assertEqual(response.status_code, 200)
    
    def test_page_list_view(self):
        response = self.client.get(reverse('pages:list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Pages')
    
    def test_add_comment(self):
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('pages:add_comment', args=['test-page']),
            {'content': 'Test comment'}
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(PageComment.objects.count(), 1)
    
    def test_add_rating(self):
        self.client.login(username='testuser', password='testpass123')
        
        response = self.client.post(
            reverse('pages:add_rating', args=['test-page']),
            {'rating': 5}
        )
        
        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertEqual(PageRating.objects.count(), 1)

class PageAdminTests(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            password='admin123',
            email='admin@example.com'
        )
        
        self.client = Client()
        self.client.login(username='admin', password='admin123')
    
    def test_admin_page_list(self):
        response = self.client.get('/admin/pages/page/')
        self.assertEqual(response.status_code, 200)
    
    def test_admin_add_page(self):
        response = self.client.post('/admin/pages/page/add/', {
            'title': 'Admin Test Page',
            'slug': 'admin-test-page',
            'content': 'Admin test content',
            'status': 'published'
        })
        self.assertEqual(response.status_code, 302)  # Redirect after save
        self.assertTrue(Page.objects.filter(slug='admin-test-page').exists())

class PageAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='apiuser',
            password='apipass123'
        )
        
        self.page = Page.objects.create(
            title='API Test Page',
            slug='api-test-page',
            content='API test content',
            status='published'
        )
    
    def test_page_api_list(self):
        response = self.client.get('/api/pages/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'API Test Page')
    
    def test_page_api_detail(self):
        response = self.client.get(f'/api/pages/{self.page.slug}/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'api-test-page')
    
    def test_page_search_api(self):
        response = self.client.get('/api/pages/search/?q=API')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(response.json()) > 0)

# Performance tests
class PagePerformanceTests(TestCase):
    def test_page_queryset_performance(self):
        # Create 1000 pages
        for i in range(1000):
            Page.objects.create(
                title=f'Performance Page {i}',
                slug=f'performance-page-{i}',
                content='Performance test content',
                status='published'
            )
        
        # Test query performance
        import time
        start_time = time.time()
        
        pages = Page.objects.filter(status='published').order_by('-created_at')[:100]
        list(pages)  # Execute query
        
        end_time = time.time()
        query_time = end_time - start_time
        
        # Query should be fast (under 0.1 seconds)
        self.assertLess(query_time, 0.1)