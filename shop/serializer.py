from rest_framework import serializers
from .models import *

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = ('id', 'title', 'image_link')

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sellers
        fields = ('id', 'title', 'log_img', 'phone_number', 'reg_date', 'city')

class SubcategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Subcategory
        fields = ('id', 'title', 'base_specifications', 'category_id')

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'title', 'description', 'subcat_id')

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ('id', 'image_link', 'product_id')

class Sellers_prodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sellers_prod
        fields = ('id', 'choice_btn', 'prod_id', 'seller_id', 'price')

class Spec_categorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Spec_category
        fields = ('id', 'name')

class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ('id', 'name', 'spec_cat_id', 'subcat_id')

class Spec_valSerializer(serializers.ModelSerializer):
    class Meta:
        model = Spec_vals
        fields = ('id', 'values', 'prod_id', 'specification_id')

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('id', 'comment', 'rating', 'date', 'author_id', 'sell_prod_id')