from django.urls import path
from . import views

urlpatterns=[
    path('',views.home,name='home'),
    path('store/',views.store,name='store'),
    path('cart/',views.cart,name='cart'),
    path('checkout/',views.checkout,name='checkout'),
    path('update_item/',views.updateItem,name='update_item'),
    path('process_order/',views.processOrder,name='process_order'),
    path('signup/',views.handlesignup,name='handlesignup'),
    path('login/',views.handlelogin,name='handlelogin'),
    path('logout/',views.handlelogout,name='handlelogout'),
    path('contact/',views.contact,name='contact'),
    path('search/',views.search,name='search'),
]
