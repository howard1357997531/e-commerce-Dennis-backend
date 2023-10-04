from django.urls import path
from base.views import order_views as views

urlpatterns = [
    path('', views.getOrders, name="getOrders"),
    path('add/', views.addOrderItems, name="addOrderItems"),
    path('getMyOrders/', views.getMyOrders, name="getMyOrders"),
    path('<str:pk>/deliver/', views.updateOrderToDelivered, name="updateOrderToDelivered"),
    path('<str:pk>/', views.getOrderById, name="getOrderById"),
    path('<str:pk>/pay/', views.updateOrderToPaid, name="updateOrderToPaid"),
]