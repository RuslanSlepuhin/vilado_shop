from django.contrib import admin

from .models import *

admin.site.register(CategoriesModel)
admin.site.register(ItemModel)
admin.site.register(CustomUser)
admin.site.register(ShoppingCartModel)
