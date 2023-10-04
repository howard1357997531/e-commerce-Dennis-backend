from django.urls import path
from base.views import user_views as views

urlpatterns = [
    # 輸入現有帳號密碼會生成專屬 token
    # 可以去 https://jwt.io/ 去解碼 token
    path('login/', views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('register/', views.registerUser, name='registerUser'),
    path('profile/', views.getUserProfile, name='getUserProfile'),
    path('profile/update/', views.updateUserProfile, name='updateUserProfile'),
    path('', views.getUsers, name='getUsers'),
    path('<str:pk>/', views.getUsersById, name='getUsersById'),
    path('update/<str:pk>/', views.updateUser, name='updateUser'),
    path('delete/<str:pk>/', views.deleteUsers, name='deleteUsers'),
]