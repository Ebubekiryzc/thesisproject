from apps.product.models import Review
from apps.product.api.serializers import ProductSerializer, ReviewSerializer
from rest_framework.viewsets import GenericViewSet
from rest_framework import mixins, permissions


class ProductAPIViewSet(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        GenericViewSet):

    serializer_class = ProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        current_user = self.request.user
        queryset = current_user.products_added_to_wishlist.all()
        return queryset

    def perform_create(self, serializer):
        serializer.save(updated_by=self.request.user)

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
