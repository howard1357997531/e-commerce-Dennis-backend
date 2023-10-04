from django.urls import path
from base.views import product_views as views

urlpatterns = [
    path('', views.getProducts, name='getProducts'),
    path('top/', views.getTopProducts, name='getTopProducts'),
    path('create/', views.createProduct, name='createProduct'),
    path('upload/', views.uploadImage, name='uploadImage'),
    path('<str:pk>/reviews/', views.createProductReview, name='createProductReview'),
    path('<str:pk>/', views.getProduct, name='getProduct'),
    path('update/<str:pk>/', views.updateProduct, name='updateProduct'),
    path('delete/<str:pk>/', views.deleteProduct, name='deleteProduct'),
]