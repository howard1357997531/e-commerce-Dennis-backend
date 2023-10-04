from django.contrib.auth.models import User
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Product, Order, OrderItem, ShippingAddress, Review

'''
serializers.SerializerMethodField(read_only=True) :
當你在字段上設置 read_only=True 時，
這意味著這個字段只會在序列化（讀取）過程中被使用。
換句話說，當你想從數據庫中讀取數據並序列化為 JSON 或其他格式時，
這個字段會被包含在序列化的結果中。然而，在反序列化（寫入）過程中，
你不能使用這個字段，因為它只是用來展示數據，而不是接收數據。
'''
class UserSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    _id = serializers.SerializerMethodField(read_only=True)
    isAdmin = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', '_id', 'username', 'email', 'name', 'isAdmin')

    # 如果直接輸入網址 http://127.0.0.1:8000/api/user/profile/ 
    # 會跑 error : AttributeError: 'AnonymousUser' object has no attribute 'first_name'
    # 要使用 postman 來做查詢
    def get_name(self, obj):
        name = obj.first_name + obj.last_name
        if name == '':
            name = obj.email
        return name
    
    def get__id(self, obj):
        return obj.id
    
    def get_isAdmin(self, obj):
        return obj.is_staff
    
    # if user reset their account information we need a new token to represent the new
    # user information 

class UserSerializerWithToken(UserSerializer):
    token = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ('id', '_id', 'username', 'email', 'name', 'isAdmin', 'token')

    def get_token(self, obj):
        token = RefreshToken.for_user(obj)
        # return str(token) # 這樣寫 token type 會是 reflash ex:{"token_type": "refresh" }
        return str(token.access_token)
class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'

class ProductSerializer(serializers.ModelSerializer):
    reviews = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Product
        fields = '__all__'

    def get_reviews(self, obj):
        reviews = obj.review_set.all()
        serializer = ReviewSerializer(reviews, many=True)
        return serializer.data

class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    orderItems = serializers.SerializerMethodField(read_only=True)
    shippingAddress = serializers.SerializerMethodField(read_only=True)
    user = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def get_orderItems(self, obj):
        # relative field 都是全小寫(即使 model 那邊是 OrderItem)
        items = obj.orderitem_set.all()
        serializer = OrderItemSerializer(items, many=True)
        return serializer.data
    
    def get_shippingAddress(self, obj):
        try:
            # 因為是OneToOneField 後面不用加 _set
            address = obj.shippingaddress
            serializer = ShippingAddressSerializer(address, many=False)
        except:
            return False
        return serializer.data
    
    def get_user(self, obj):
        user = obj.user
        serializer = UserSerializer(user, many=False)
        return serializer.data

class ShippingAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShippingAddress
        fields = '__all__'




