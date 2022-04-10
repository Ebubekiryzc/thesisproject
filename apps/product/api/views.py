from django.forms import ValidationError
from apps.product.models import Product, Review
from apps.product.api.serializers import ProductSerializer, ReviewSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework.response import Response
from rest_framework import mixins, permissions, status


class ProductAPIViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):

    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        current_user = self.request.user
        queryset = current_user.products_added_to_wishlist.all()
        return queryset

    def create(self, request):
        current_user = self.request.user
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        instance_link = serializer.validated_data['product_link']
        product_occurence = Product.objects.safe_get(instance_link)

        if product_occurence:
            if current_user.products_added_to_wishlist.filter(product_link=instance_link).exists():
                return Response({'message': 'Bu ürün zaten istek listenizde mevcut.', 'data': self.get_serializer(product_occurence).data}, status=status.HTTP_200_OK)
            else:
                product_occurence.updated_by = current_user
                product_occurence.save()
                return Response({'message': 'Ürün başarıyla istek listesine eklendi.', 'data': self.get_serializer(product_occurence).data}, status=status.HTTP_200_OK)
        else:
            try:
                serializer.save(updated_by=self.request.user)
            except ValidationError as e:
                return Response({'message': f'{e.message}', 'data': serializer.validated_data}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'message': f'Ürün başarıyla eklendi.', 'data': serializer.validated_data}, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        current_user = self.request.user
        current_user.products_added_to_wishlist.remove(instance)

    # lookup_field = 'id'
    # filter_backends = [SearchFilter]
    # search_fields = ['product_description']


class ProductReviewAPIViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        GenericViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]
