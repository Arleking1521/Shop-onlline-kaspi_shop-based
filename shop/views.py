from django.shortcuts import render
from .models import *
from django.db.models import Avg, Min, Q, Count
import math

# Create your views here.
def AllCategories(request):
    categories = Categories.objects.order_by('id')
    return render(request, 'shop/CategoryPage.html', {'categories': categories})

def SubCategories(request, cid, subid=-1):
    if subid == -1:
        subcategories = Subcategory.objects.filter(category_id=cid).order_by('id')
    else:
        subcategories = [Subcategory.objects.get(id=subid)]
    products =[]
    for subcategory in subcategories:
        prods = Product.objects.filter(subcat_id=subcategory.pk)
        for prod in prods:
            products.append(prod)
    sellers_prods = []
    for product in products:
        sell_prods = Sellers_prod.objects.filter(prod_id=product.pk)

        if not sell_prods.exists():
            continue
        
        image = Images.objects.filter(product_id = product.pk).first()

        min_price = sell_prods.aggregate(minimum = Min('price'))['minimum'] or 0
        reviews= Review.objects.filter(sell_prod__in = sell_prods)
        avg_rate = reviews.aggregate(average=Avg('rating'))['average'] or 0

        dict_product = {
            'product':product,
            'image': image.image_link if image else None,
            'min_price': min_price,
            'review_rate':math.ceil(avg_rate),
            'review_count':len(reviews),
        }
        
        sellers_prods.append(dict_product)
    
    return render(request, 'shop/SubCategoryPage.html', {'subcat': subcategories, 'products': sellers_prods, 'cid':cid})

def DetailsPage(request, pid):
    product = Product.objects.get(id=pid)
    images = Images.objects.filter(product_id=product.pk)
    sellers_prods = Sellers_prod.objects.filter(prod_id=product.pk).order_by('price')
    min_price = sellers_prods.aggregate(minimum = Min('price'))['minimum'] or 0
    reviews= Review.objects.filter(sell_prod__in = sellers_prods).order_by('-date')
    avg_rate = reviews.aggregate(average=Avg('rating'))['average'] or 0

    info = {
        'product' : product,
        'images' : images,
        'min_price' : min_price,
        'avg_rate' : avg_rate,
        'review_count' : reviews.count()
    }

    specifics = Spec_vals.objects.filter(prod_id = pid)
    spec = []
    for specific in specifics:
        specif = Specification.objects.get(pk=specific.specification_id)
        sp = {
            'spec_cat' : Spec_category.objects.get(pk=specif.spec_cat_id).name,
            'spec_name' : specif.name,
            'value' : specific.values
        }
        spec.append(sp)

    specifications = {}
    for s in spec:
        if s['spec_cat'] in specifications.keys():
            specifications[s['spec_cat']].append(s)
        else:
            specifications[s['spec_cat']]=[s]

    print(list(specifications.items()))

    reviews_tab = reviews

    shops =  []
    for seller_prod in sellers_prods:
        reviews = Review.objects.filter(sell_prod_id = seller_prod.pk)
        shop = {
            'seller' : Sellers.objects.get(pk=seller_prod.seller_id),
            'price' : seller_prod.price,
            'rating' :  reviews.aggregate(average=Avg('rating'))['average'] or 0,
            'reviews_count': reviews.count()
        } 
        shops.append(shop)


    return render(request, 'shop/ProductDetails.html', {'info' : info, 'specifics': spec, 'shops': shops, 'reviews': reviews_tab, 'specifications' : list(specifications.items())})

def SellerDetails(request, sid):
    seller = Sellers.objects.get(pk=sid)
    sell_prods = Sellers_prod.objects.filter(seller_id=sid)
    all_reviews = Review.objects.filter(sell_prod__in = sell_prods).order_by('-date')
    avg_rate = all_reviews.aggregate(average=Avg('rating'))['average'] or 0
    return render(request, 'shop/SellerPage.html', {'seller_info' : seller, 'reviews': all_reviews, 'avg_rate': avg_rate})

# --------------------------------------DRF------------------------------------------------------------------------------------------------

from rest_framework.views import APIView
from .serializer import *
# from rest_framework.response import Response
from django.http import JsonResponse
from rest_framework import status

site_host='http://194.110.55.14'

class CategoriesView(APIView):
    def get(self, request):
        categories = Categories.objects.all()
        serialized = CategorySerializer(categories, many=True)
        for category in serialized.data:
            if category['image_link']:
                category['image_link'] = f'{site_host}{category["image_link"]}'
        return JsonResponse(serialized.data, safe = False)

    def post(self, request):
        serialized = CategorySerializer(data=request.data)
        if serialized.is_valid(raise_exception=True):
            serialized.save()
            return JsonResponse(serialized.data, status = status.HTTP_201_CREATED)

class CategoryView(APIView):
    def get(self, request, cid):
        try:
            category = Categories.objects.get(id=cid)
            serialized = CategorySerializer(category)
            data = serialized.data
            if data['image_link']:
                data['image_link'] = f'{site_host}{data["image_link"]}'
            return JsonResponse(data)
        except:
            return JsonResponse({"error": "Category with this ID not found"}, status = status.HTTP_404_NOT_FOUND)

    def put(self, request, cid):
        try:
            category = Categories.objects.get(id=cid)
            serialized = CategorySerializer(category, data=request.data)
            if serialized.is_valid():
                serialized.save()
                return JsonResponse(serialized.data)
            return JsonResponse(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return JsonResponse({"error": "Category with this ID not found"}, status = status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, cid):
        try:
            category = Categories.objects.get(id=cid)
            category.delete()
            return JsonResponse({"message: Category was deleted"}, status=status.HTTP_204_NO_CONTENT)
        except:
            return JsonResponse({"error": "Category with this ID not found"}, status = status.HTTP_404_NOT_FOUND)


class SubCategoriesView(APIView):
    def get(self, request):
        category_id = request.query_params.get('category_id')
        if category_id:
            subcategories = Subcategory.objects.filter(category__id=category_id)
        else:
            subcategories = Subcategory.objects.all()
        serialized = SubcategorySerializer(subcategories, many=True)
        return JsonResponse(serialized.data, safe=False)

    def post(self, request):
        serialized = SubcategorySerializer(data=request.data)
        if serialized.is_valid():
            serialized.save()
            return JsonResponse(serialized.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
        
class SubCategoryView(APIView):
    def get(self, request, scid):
        try:
            subcategory = Subcategory.objects.get(id=scid)
            serialized = SubcategorySerializer(subcategory)
            return JsonResponse(serialized.data)
        except:
            return JsonResponse({"error": "Subcategory with this ID not found"}, status = status.HTTP_404_NOT_FOUND)

    def put(self, request, scid):
        try:
            subcategory = Subcategory.objects.get(id=scid)
            serialized = SubcategorySerializer(subcategory, data=request.data)
            if serialized.is_valid():
                serialized.save()
                return JsonResponse(serialized.data)
            return JsonResponse(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return JsonResponse({"error": "Subcategory with this ID not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, scid):
        try:
            subcategory = Subcategory.objects.get(id=scid)
            subcategory.delete()
            return JsonResponse({"message : Subcategory was deleted"}, status=status.HTTP_204_NO_CONTENT)
        except:
            return JsonResponse({"error": "Subcategory with this ID not found"}, status=status.HTTP_404_NOT_FOUND)

class SellersView(APIView):
    def get(self, request):
        seller = Sellers.objects.all()
        serialized = SellerSerializer(seller, many=True)
        for seller in serialized.data:
            if seller['log_img']:
                seller['log_img'] = f'{site_host}{seller["log_img"]}'
        return JsonResponse(serialized.data, safe = False)
    
    def post(self, request):
        serialized = SellerSerializer(data=request.data)
        if serialized.is_valid(raise_exception=True):
            serialized.save()
            return JsonResponse(serialized.data, status=status.HTTP_201_CREATED)

class SellerView(APIView):
    def get(self, request, sid):
        try:
            seller = Sellers.objects.get(id=sid)
            serialized = SellerSerializer(seller)
            data = serialized.data
            if data['log_img']:
                data['log_img'] = f'{site_host}{data["log_img"]}'
            return JsonResponse(data)
        except:
            return JsonResponse({"error": "Seller with this ID not found"}, status = status.HTTP_404_NOT_FOUND)
        
    def put(self, request, sid):
        try:
            seller = Sellers.objects.get(id=sid)
            serialized = SellerSerializer(seller, data=request.data)
            if serialized.is_valid():
                serialized.save()
                return JsonResponse(serialized.data)
            return JsonResponse(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return JsonResponse({"error": "Seller with this ID not found"}, status = status.HTTP_404_NOT_FOUND)

    def delete(self, request, sid):
        try:
            seller = Sellers.objects.get(id=sid)
            seller.delete()
            return JsonResponse({"message: Seller was deleted"}, status=status.HTTP_204_NO_CONTENT)
        except:
            return JsonResponse({"error": "Seller with this ID not found"}, status = status.HTTP_404_NOT_FOUND)


class ProductsView(APIView):
    def get(self, request):
        subcat_id = request.query_params.get('subcat_id')
        cat_id = request.query_params.get('cat_id')
        queryset = Product.objects.all()
        if subcat_id:
            queryset = queryset.filter(subcat__id=subcat_id)
        elif cat_id:
            queryset = queryset.filter(subcat__category__id=cat_id)
        queryset = queryset.annotate(
            calculated_min_price=Min(
                'sellers_prod__price', 
                filter=Q(sellers_prod__choice_btn=True)
            ),
            calculated_average_rating=Avg('sellers_prod__review__rating') 
        )
        queryset = queryset.prefetch_related(
            'spec_vals_set',
            'spec_vals_set__specification'
        )
        serialized = ProductSerializer(queryset, many=True)
        return JsonResponse(serialized.data, safe=False)

    def post(self, request):
        serialized = ProductSerializer(data=request.data)
        if serialized.is_valid():
            serialized.save()
            return JsonResponse(serialized.data, status=status.HTTP_201_CREATED)
        
        return JsonResponse(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductView(APIView):
    def get(self, request, pid):
        product = Product.objects.filter(id=pid).annotate(
            calculated_min_price=Min('sellers_prod__price', filter=Q(sellers_prod__choice_btn=True)),
            calculated_average_rating=Avg('sellers_prod__review__rating'),
            calculated_review_count=Count('sellers_prod__review') 
        ).prefetch_related(
            'images_set',
            'sellers_prod_set',
            'sellers_prod_set__seller',
            'spec_vals_set',
            'spec_vals_set__specification',
            'spec_vals_set__specification__spec_cat'
        ).first()
        
        if product is None:
             return JsonResponse({"error": "Product with this ID not found"}, status=status.HTTP_404_NOT_FOUND)
        serialized = ProductDetailSerializer(product)
        return JsonResponse(serialized.data)


class ImagesView(APIView):
    def get(self, request):
        image = Images.objects.all()
        serialized = ImageSerializer(image, many=True)
        return JsonResponse(serialized.data, safe = False)

    def post(self, request):
        serialized = ImageSerializer(data=request.data)
        if serialized.is_valid(raise_exception=True):
            serialized.save()
            return JsonResponse(serialized.data, status=status.HTTP_201_CREATED)

class ImageView(APIView):
    def get(self, request, iid):
        try:
            image = Images.objects.get(id=iid)
            serialized = ImageSerializer(image)
            return JsonResponse(serialized.data)
        except:
            return JsonResponse({"error : Image with this ID not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, iid):
        try:
            image = Images.objects.get(id=iid)
            serialized = ImageSerializer(image, data=request.data)
            if serialized.is_valid():
                serialized.save()
                return JsonResponse(serialized.data)
            return JsonResponse(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return JsonResponse({"errors : Image with this ID not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, iid):
        try:
            image = Images.objects.get(id=iid)
            image.delete()
            return JsonResponse({"Image was deleted"}, status=status.HTTP_204_NO_CONTENT)
        except:
            return JsonResponse({"error : Image with this ID not found"}, status=status.HTTP_404_NOT_FOUND)




class Sellers_prodsView(APIView):
    def get(self,request):
        seller_prod = Sellers_prod.objects.all()
        serialized = Sellers_prodSerializer(seller_prod, many=True)
        return JsonResponse(serialized.data, safe = False)
    
    def post(self, request):
        serialized = Sellers_prodSerializer(data=request.data)
        if serialized.is_valid(raise_exception=True):
            serialized.save()
            return JsonResponse(serialized.data, status=status.HTTP_201_CREATED)

class Seller_prodView(APIView):
    def get(self,request, spid):
        try:
            seller_prod = Sellers_prod.objects.get(id=spid)
            serialized = Sellers_prodSerializer(seller_prod)
            return JsonResponse(serialized.data)
        except:
            return JsonResponse({"error : Seller prod with this ID not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self,request, spid):
        try:
            seller_prod = Sellers_prod.objects.get(id=spid)
            serialized = Sellers_prodSerializer(seller_prod, data=request.data)
            if serialized.is_valid():
                serialized.save()
                return JsonResponse(serialized.data)
            return JsonResponse(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return JsonResponse({"error : Seller prod with this ID not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, spid):
        try:
            seller_prod = Sellers_prod.objects.get(id=spid)
            seller_prod.delete()
            return JsonResponse({"Seller prod was deleted"}, status=status.HTTP_204_NO_CONTENT)
        except:
            return JsonResponse({"error : Sellers prod with this ID not found"}, status=status.HTTP_404_NOT_FOUND)


class Spec_categoriesView(APIView):
    def get(self, request):
        spec_category = Spec_category.objects.all()
        serialized = Spec_categorySerializer(spec_category, many=True)
        return JsonResponse(serialized.data, safe = False)
    
    def post(self, request):
        serialized = Spec_categorySerializer(data=request.data)
        if serialized.is_valid(raise_exception=True):
            serialized.save()
            return JsonResponse(serialized.data, status=status.HTTP_201_CREATED)

class Spec_categoryView(APIView):
    def get(self, request, scid):
        try:
            spec_category = Spec_category.objects.get(id=scid)
            serialized = Spec_categorySerializer(spec_category)
            return JsonResponse(serialized.data)
        except:
            return JsonResponse({"error : Spec category with this ID not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def put(self, request, scid):
        try:
            spec_category = Spec_category.objects.get(id=scid)
            serialized = Spec_categorySerializer(spec_category, data=request.data)
            if serialized.is_valid():
                serialized.save()
                return JsonResponse(serialized.data)
            return JsonResponse(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return JsonResponse({"error : Spec category with this ID not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, scid):
        try:
            spec_category = Spec_category.objects.get(id=scid)
            spec_category.delete()
            return JsonResponse({"Spec category was deleted"}, status=status.HTTP_204_NO_CONTENT)
        except:
            return JsonResponse({"error : Spec category with this ID not found"}, status=status.HTTP_404_NOT_FOUND)




class SpecificationsView(APIView):
    def get(self, request):
        specification = Specification.objects.all()
        serialized = SpecificationSerializer(specification, many=True)
        return JsonResponse(serialized.data, safe = False)
    
    def post(self,request):
        serialized = Spec_categorySerializer(data=request.data)
        if serialized.is_valid(raise_exception=True):
            serialized.save()
            return JsonResponse(serialized.data, status=status.HTTP_201_CREATED)

class SpecificationView(APIView):
    def get(self,request, sid):
        try:    
            specification = Specification.objects.get(id=sid)
            serialized = SpecificationSerializer(specification)
            return JsonResponse(serialized.data)
        except:
            return JsonResponse({"error : Specification with this ID not found"}, status=status.HTTP_404_NOT_FOUND)

    def put(self,request, sid):
        try: 
            specification = Specification.objects.get(id=sid)
            serialized = SpecificationSerializer(specification, data=request.data)
            if serialized.is_valid():
                serialized.save()
                return JsonResponse(serialized.data)
            return JsonResponse(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return JsonResponse("error : Specification with this ID not found", status=status.HTTP_404_NOT_FOUND)

    def delete(self,request, sid):
        try:
            specification = Specification.objects.get(id=sid)
            specification.delete()
            return JsonResponse({"Specification was deleted"}, status=status.HTTP_204_NO_CONTENT)
        except:
            return JsonResponse("error : Specification with this ID not found", status=status.HTTP_404_NOT_FOUND)


class Spec_valsView(APIView):
    def get(self, request):
        spec_vals = Spec_vals.objects.all()
        serialized = Spec_valSerializer(spec_vals, many=True)
        return JsonResponse(serialized.data, safe = False)
    
    def post(self,request):
        serialized = Spec_valSerializer(data=request.data)
        if serialized.is_valid(raise_exception=True):
            serialized.save()
            return JsonResponse(serialized.data, status=status.HTTP_201_CREATED)
        
class Spec_valView(APIView):
    def get(self,request, svid):
        try:
            spec_val = Spec_vals.objects.get(id=svid)
            serialized = Spec_valSerializer(spec_val)
            return JsonResponse(serialized.data)
        except:
            return JsonResponse({"error : Spec val with this ID was not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def put(self,request, svid):
        try:
            spec_val = Spec_vals.objects.get(id=svid)
            serialized = Spec_valSerializer(spec_val, data=request.data)
            if serialized.is_valid():
                serialized.save()
                return JsonResponse(serialized.data)
            return JsonResponse(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return JsonResponse({"error : Spec val with this ID not found"}, status=status.HTTP_404_NOT_FOUND)

    def delete(self,request, svid):
        try:
            spec_val = Spec_vals.objects.get(id=svid)
            spec_val.delete()
            return JsonResponse({"Spec val was deleted"}, status=status.HTTP_204_NO_CONTENT)
        except:
            return JsonResponse({"error : Spec val with this ID not found"}, status=status.HTTP_404_NOT_FOUND)



class ReviewsView(APIView):
    def get(self,request):
        review = Review.objects.all()
        serialized = ReviewSerializer(review, many=True)
        return JsonResponse(serialized.data, safe = False)
    
    def post(self,request):
        serialized = ReviewSerializer(data=request.data)
        if serialized.is_valid(raise_exception=True):
            serialized.save()
            return JsonResponse(serialized.data, status=status.HTTP_201_CREATED)
        
class ReviewView(APIView):
    def get(self,request, rid):
        try:
            review = Review.objects.get(id=rid)
            serialized = ReviewSerializer(review)
            return JsonResponse(serialized.data)
        except:
            return JsonResponse({"error : Review with this ID not found"}, status=status.HTTP_404_NOT_FOUND)
        
    def put(self,request, rid):
        try:
            review = Review.objects.get(id=rid)
            serialized = ReviewSerializer(review, data=request.data)
            if serialized.is_valid():
                serialized.save()
                return JsonResponse(serialized.data)
            return JsonResponse(serialized.errors, status=status.HTTP_400_BAD_REQUEST)
        except:
            return JsonResponse({"error : Review with this ID not found"}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, rid):
        try:
            review = Review.objects.get(id=rid)
            review.delete()
            return JsonResponse({"Review was deleted"}, status=status.HTTP_204_NO_CONTENT)
        except:
            return JsonResponse({"error : Review with this ID not found"}, status=status.HTTP_404_NOT_FOUND)