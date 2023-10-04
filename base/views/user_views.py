from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework import status
from base.serializers import UserSerializer, UserSerializerWithToken
from typing import Any, Dict

class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    # @classmethod
    # def get_token(cls, user):
    #     token = super().get_token(user)
    #     token['username'] = user.username
    #     token['message'] = 'hello'

    #     return token

    # 可以去 djangorestframework-simplejwt github 複製原始碼來做修改
    # https://github.com/jazzband/djangorestframework-simplejwt/blob/master/rest_framework_simplejwt/serializers.py
    # 照樣寫可以不用去 decode token 就可以得到 'username' 等等的資訊
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, str]:
        data = super().validate(attrs)
        # data['username'] = self.user.username
        # data['email'] = self.user.email

        serializer = UserSerializerWithToken(self.user).data
        for key, value in serializer.items():
            data[key] = value
        return data
    
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer

@api_view(['POST'])
def registerUser(request):
    data = request.data
    try:
        user = User.objects.create(
            first_name = data.get('name'),
            username = data.get('email'),
            email = data.get('email'),
            password = make_password(data.get('password'))
        )
        serializer = UserSerializerWithToken(user, many=False)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    except:
        message = {'detail': 'User with this email already exists'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    # 因為在 settings 'DEFAULT_AUTHENTICATION_CLASSES' 有設定，所以要取得auth資料要在 header 
    # 寫入 key: Authorization , valie: Bearer (access token)
    user = request.user
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUserProfile(request):
    user = request.user
    # 更新使用者資料需要得到新的 token
    serializer = UserSerializerWithToken(user, many=False)

    data = request.data
    user.first_name = data.get('name')
    user.username = data.get('email')
    user.email = data.get('email')
    if data.get('password') != '':
        user.password = make_password(data.get('password'))

    user.save()
    return Response(serializer.data)

# @permission_classes([IsAdminUser]) 需要超級使用才能觀看
# 要在 header 寫入 key: Authorization , valie: Bearer (access token)
# jwt decode 後是超級使用者情況下可以寬看
@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUsersById(request, pk):
    user = User.objects.filter(id=pk).first()
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUser(request, pk):
    user = User.objects.filter(id=pk).first()
    data = request.data
    user.first_name = data.get('name')
    user.username = data.get('email')
    user.email = data.get('email')
    user.is_staff = data.get('isAdmin')
    user.save()

    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteUsers(request, pk):
    userForDeletion = User.objects.filter(id=pk).first()
    userForDeletion.delete()
    return Response({'User was delete'})

