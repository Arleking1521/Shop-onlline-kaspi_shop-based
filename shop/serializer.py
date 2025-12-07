from rest_framework import serializers
from .models import *
from django.db.models import Min, Avg, Count 

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
    min_price = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    category_id = serializers.IntegerField(source='subcat.category_id', read_only=True)
    specifications = Spec_valSerializer(source='spec_vals_set', many=True, read_only=True)
    main_image = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = ('id', 'title', 'description', 'subcat_id', 'min_price', 'average_rating', 'category_id', 'review_count', 'main_image' 'specifications')
    def get_main_image(self, obj):
        first_image = obj.images_set.order_by('id').values('image_link').first()
        if first_image:
            return first_image['image_link']
        return None
    def get_review_count(self, obj):
        if hasattr(obj, 'calculated_review_count'):
            return obj.calculated_review_count
        return obj.sellers_prod_set.aggregate(count=Count('review'))['count']
    def get_min_price(self, obj):
        if hasattr(obj, 'calculated_min_price'):
            return obj.calculated_min_price
        aggregation = obj.sellers_prod_set.aggregate(min_price=Min('price'))
        return aggregation.get('min_price')
    def get_average_rating(self, obj):
        if hasattr(obj, 'calculated_average_rating'):
            return obj.calculated_average_rating
        aggregation = Review.objects.filter(
            sell_prod__prod=obj
        ).aggregate(avg_rating=Avg('rating'))
        return aggregation.get('avg_rating')

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Images
        fields = ('id', 'image_link', 'product_id')

class Sellers_prodSerializer(serializers.ModelSerializer):
    seller_detail = SellerSerializer(source='seller', read_only=True)
    class Meta:
        model = Sellers_prod
        fields = ('id', 'choice_btn', 'prod_id', 'seller_id', 'price', 'seller_detail')

class Spec_categorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Spec_category
        fields = ('id', 'name')

class SpecificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Specification
        fields = ('id', 'name', 'spec_cat_id', 'subcat_id')

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = ('id', 'comment', 'rating', 'date', 'author_id', 'sell_prod_id')

class Spec_valSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='specification.name', read_only=True)
    spec_category = Spec_categorySerializer(source='specification.spec_cat', read_only=True)
    class Meta:
        model = Spec_vals
        fields = ('id', 'values', 'prod_id', 'specification_id', 'name', 'spec_category')


class ProductDetailSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(source='subcat.category_id', read_only=True) 
    min_price = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField() 
    review_count = serializers.SerializerMethodField()
    main_image = serializers.SerializerMethodField() 
    images = ImageSerializer(source='images_set', many=True, read_only=True)
    specifications = Spec_valSerializer(source='spec_vals_set', many=True, read_only=True) 
    sellers_prod = Sellers_prodSerializer(source='sellers_prod_set', many=True, read_only=True)
    class Meta:
        model = Product
        fields = (
            'id', 'title', 'description', 'subcat_id', 'category_id',
            'min_price', 'average_rating', 'review_count', 'main_image',
            'images', 'specifications', 'sellers_prod'
        )