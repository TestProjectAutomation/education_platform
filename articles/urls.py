from django.urls import path
from . import views

app_name = 'articles'

urlpatterns = [
    # الصفحات الرئيسية
    path('', views.article_list, name='list'),
    path('search/', views.article_search, name='search'),
    path('archive/', views.article_archive, name='archive'),
    
    # المقالات حسب التصنيفات والوسوم
    path('category/<slug:slug>/', views.article_by_category, name='category'),
    path('tag/<slug:slug>/', views.article_by_tag, name='tag'),
    
    # المقالات المميزة
    path('featured/', views.featured_articles, name='featured'),
    path('popular/', views.popular_articles, name='popular'),
    path('latest/', views.latest_articles, name='latest'),
    
    # المقالات المفردة
    path('<slug:slug>/', views.article_detail, name='detail'),
    path('<slug:slug>/rate/', views.rate_article, name='rate'),
    path('<slug:slug>/bookmark/', views.bookmark_article, name='bookmark'),
    path('<slug:slug>/share/', views.share_article, name='share'),
    path('<slug:slug>/print/', views.print_article, name='print'),
    
    # التعليقات
    path('<slug:slug>/comment/', views.add_comment, name='add_comment'),
    path('comment/<int:pk>/reply/', views.add_reply, name='add_reply'),
    path('comment/<int:pk>/vote/', views.vote_comment, name='vote_comment'),
    
    # التقارير والإحصائيات
    path('stats/', views.article_statistics, name='stats'),
    path('sitemap.xml', views.article_sitemap, name='sitemap'),
    path('rss/', views.article_rss_feed, name='rss_feed'),
]
