from apps.product.models import Product, Review
from rest_framework import serializers


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('id', 'body', 'processed_body')


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = (
            "id",
            "product_description",
            "product_original_price",
            "product_discounted_price",
            "product_picture_source",
            "product_mean_rating",
            "product_review_count",
            "updated_by")
