from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from base.models import Product, Review
from base.serializers import ProductSerializer

@api_view(['GET'])
def getProducts(request):
    query = request.query_params.get('keyword') if request.query_params.get('keyword') != None else ""
    # print(query); print(request.query_params)

    # name__icontains="" 可以抓到全部 name
    products = Product.objects.filter(name__icontains=query)
    page = request.query_params.get('page')
    paginator = Paginator(products, 2)

    try:
        products = paginator.page(page)
    except PageNotAnInteger:
        products = paginator.page(1)
    except EmptyPage:
        products = paginator.page(paginator.num_pages)

    if page == None:
        page = 1

    page = int(page)
    # many=True : serializer multiple object
    serializer = ProductSerializer(products, many=True)
    return Response({'products': serializer.data,
                     'page': page,
                     'pages': paginator.num_pages})

@api_view(['GET'])
def getTopProducts(request):
    products = Product.objects.filter(rating__gte=4).order_by('-rating')
    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def getProduct(request, pk):
    product = Product.objects.get(_id=pk)
    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def createProduct(request):
    product = Product.objects.create(
        user = request.user,
        name = 'qwe',
        price = 0,
        brand = 'asd',
        countInStock = 0,
        category = 'qwe',
        description = ''
    )
    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data)

@api_view(['PUT'])
@permission_classes([IsAdminUser])
def updateProduct(request, pk):
    data = request.data
    product = Product.objects.filter(_id=int(pk)).first()
    product.name = data.get('name')
    product.price = data.get('price')
    product.brand = data.get('brand')
    product.countInStock = data.get('countInStock')
    product.category = data.get('category')
    product.description = data.get('description')
    product.save()

    serializer = ProductSerializer(product, many=False)
    return Response(serializer.data)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteProduct(request, pk):
    product = Product.objects.filter(_id=int(pk)).first()
    product.delete()
    return Response('Producted Deleted')

@api_view(['POST'])
def uploadImage(request):
    data = request.data
    product_id = data.get('product_id')
    product = Product.objects.filter(_id=product_id).first()
    product.image = request.FILES.get('image')
    product.save()

    return Response('Image was uploaded')

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def createProductReview(request, pk):
    product = Product.objects.filter(_id=int(pk)).first()
    user = request.user
    data = request.data
    alreadyExists = product.review_set.filter(user=request.user).exists()

    if alreadyExists:
        content = {'detail': 'Product already Review'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    elif data.get('rating') == 0:
        content = {'detail': 'Please Select a rating'}
        return Response(content, status=status.HTTP_400_BAD_REQUEST)
    else:
        Review.objects.create(
            user=user,
            product=product,
            name=user.first_name,
            rating=data.get('rating'),
            comment=data.get('comment'),
        )

        reviews = product.review_set.all()
        product.numReviews = len(reviews)
        total = 0
        for r in reviews:
            total += r.rating
        product.rating = total / len(reviews)
        product.save()

        return Response({'detail': 'Review Added'})


