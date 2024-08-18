from rest_framework import serializers
from .models import *

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"

class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemModel
        fields = "__all__"

class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoriesModel
        fields = "__all__"

class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCartModel
        fields = "__all__"
