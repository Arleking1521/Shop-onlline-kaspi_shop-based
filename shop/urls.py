from django.urls import path
from .views import *

urlpatterns = [
     path('', AllCategories, name='all_categories'),
     path('shop/category-<int:cid>/', SubCategories, name='sub_categories'),
     path('shop/category-<int:cid>/subcategory-<int:subid>', SubCategories, name='sub_category'),
     path('shop/product=<int:pid>/', DetailsPage, name='details_page'),
     path('shop/seller=<int:sid>/', SellerDetails, name='seller_details'),
     # ------------------------DRF------------------------------------------
     path('api/categories/', CategoriesView.as_view(), name='api_categories'),
     path('api/categories/<int:cid>/', CategoryView.as_view(), name='api_category'),
     path('api/subcategories/', SubCategoriesView.as_view(), name='api_subcategories'),
     path('api/subcategories/<int:scid>/', SubCategoryView.as_view(), name='api_subcategory'),
     path('api/sellers/', SellersView.as_view(), name='api_sellers'),
     path('api/sellers/<int:sid>/', SellerView.as_view(), name='api_seller'),
     path('api/products/', ProductsView.as_view(), name='api_products'),
     path('api/products/<int:pid>/', ProductView.as_view(), name='api_product'),
     path('api/images/', ImagesView.as_view(), name='api_images'),
     path('api/images/<int:iid>/', ImageView.as_view(), name='api_image'),
     path('api/sellersproduct/', Sellers_prodsView.as_view(), name='api_sellers_prod'),
     path('api/sellersproduct/<int:spid>/', Seller_prodView.as_view(), name='api_seller_prod'),
     path('api/speccategories/', Spec_categoriesView.as_view(), name='api_spec_categories'),
     path('api/speccategories/<int:scid>/', Spec_categoryView.as_view(), name='api_spec_category'),
     path('api/specifications/', SpecificationsView.as_view(), name='api_specifications'),
     path('api/specifications/<int:sid>/', SpecificationView.as_view(), name='api_specification'),
     path('api/spec-vals/', Spec_valsView.as_view(), name='api_spec_vals'),
     path('api/spec-vals/<int:svid>/', Spec_valView.as_view(), name='api_spec_val'),
     path('api/reviews/', ReviewsView.as_view(), name='api_reviews'),
     path('api/reviews/<int:rid>/', ReviewView.as_view(), name='api_review'),
]
