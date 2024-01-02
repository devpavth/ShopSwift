from django.urls import path,include
from . import views

urlpatterns=[
    path('',views.store,name='store'),
    path('cart/',views.cart,name='cart'),
    path('checkout/',views.checkout,name='checkout'),

    path('update_item/',views.updateItem,name='update_item'),
    path('process_order/',views.processOrder,name='process_order'),

    path('register/',views.registerPage,name="register"),
    path('login/',views.loginPage,name="login"),
    path('logout/',views.logoutUser,name="logout"),

    path('product/<int:product_id>/',views.productDetailsView,name='product_details'),
    path('review-page/<int:product_id>/', views.reviewPage, name='review-page'),

    path('success/', views.successMsg, name='success'),
    path('cancel/', views.payment_cancelled, name='cancel'),
]