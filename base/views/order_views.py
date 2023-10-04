from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from base.models import Product, Order, OrderItem, ShippingAddress
from base.serializers import ProductSerializer, OrderSerializer, OrderItemSerializer
from datetime import datetime

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def addOrderItems(request):
    user = request.user
    data = request.data
    orderItems = data.get('orderItems')

    if orderItems and len(orderItems) == 0:
        return Response({"detail": "No Order Item"}, status=status.HTTP_400_BAD_REQUEST)
    else:
        order = Order.objects.create(
            user=user,
            paymentMethod=data.get('paymentMethod'),
            taxPrice=data.get('taxPrice'),
            shippingPrice=data.get('shippingPrice'),
            totalPrice=data.get('totalPrice'),
        )

        ShippingAddress.objects.create(
            order = order,
            address=data.get('shippingAddress').get('address'),
            city=data.get('shippingAddress').get('city'),
            postalCode=data.get('shippingAddress').get('postalCode'),
            country=data.get('shippingAddress').get('country'),
        )

        for i in orderItems:
            product = Product.objects.filter(_id=i.get('product')).first()

            item = OrderItem.objects.create(
                product=product,
                order=order,
                name=product.name,
                qty=i.get('qty'),
                price=i.get('price'),
                image=product.image.url,
            )

            product.countInStock -= item.qty
            product.save()

    serializer = OrderSerializer(order, many=False)

    return Response(serializer.data)

@api_view(['GET'])
def getOrderById(request, pk):
    user = request.user
    order = Order.objects.get(_id=int(pk))

    # 直接用 http://127.0.0.1:8000/api/orders/1/ 在網頁上會404原因是
    # 因為前後台已經分離，所以就算前台有login也不關後台的事
    # user.is_authenticated = False
    # order.user = howard@yahoo.com.tw
    # user = AnonymousUser
    try:
        if user.is_authenticated or order.user == user:
            serializer = OrderSerializer(order, many=False)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            Response({"detail": "Not authorized to view this order"}, status=status.HTTP_400_BAD_REQUEST)
    except:
       return Response({"detail": "Order is not exists"}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getMyOrders(request):
    user = request.user
    orders = user.order_set.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def getOrders(request):
    orders = Order.objects.all()
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateOrderToPaid(request, pk):
    order = Order.objects.get(_id=pk)

    order.isPaid = True
    order.paidAt = datetime.now()
    order.save()
    return Response({'Order was paid'})

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateOrderToDelivered(request, pk):
    order = Order.objects.filter(_id=int(pk)).first()

    order.isDelivered = True
    order.deliveredAt = datetime.now()
    order.save()
    return Response({'Order was delivered'})

