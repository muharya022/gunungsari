from django.urls import path
from . import views

urlpatterns = [
    path('', views.news_list, name='new_list'),
    path('create/', views.create_article, name='create_article'),
    path('<int:pk>/', views.article_detail, name='article_detail'),
    path('categories/create/ajax/', views.create_category_ajax, name='create_category_ajax'),
    path('article/delete/<int:pk>/', views.delete_article, name='delete_article'),
    path('category/delete/<int:pk>/', views.delete_category, name='delete_category'),
]
