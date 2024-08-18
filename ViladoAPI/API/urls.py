from django.urls import path

from .views import *

urlpatterns = [
    # path('api/register/', CreateUserView.as_view(), name='create_user'),
    path('user/', CustomUserView.as_view(), name='user'),
    path('items/', ItemView.as_view(), name='items'),
    path('categories/', CategoryView.as_view(), name='category'),
    path('shopping-cart/', ShoppingCartView.as_view(), name='shopping_cart'),

]
