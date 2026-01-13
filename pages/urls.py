from django.urls import path, include
from django.contrib.sitemaps.views import sitemap
from . import views

app_name = 'pages'



urlpatterns = [
    # Basic pages
    path('', views.page_list, name='list'),
    path('search/', views.page_search, name='search'),
    
    # Page detail with comments and ratings
    path('<slug:slug>/', views.page_detail, name='detail'),
    path('<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('<slug:slug>/rate/', views.add_rating, name='add_rating'),
    path('<slug:slug>/preview/', views.page_preview, name='preview'),
    
    # Sitemap
    path('sitemap.xml', views.page_sitemap, name='sitemap'),
    
    # Class-based views (alternative)
    path('cbv/', views.PageListView.as_view(), name='list_cbv'),
    path('cbv/<slug:slug>/', views.PageDetailView.as_view(), name='detail_cbv'),
    
]
