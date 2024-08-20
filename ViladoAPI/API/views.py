from django.forms import model_to_dict
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response

# from variables.bot_dialog import empty_base
from .models import *
from .serializers import *

class CustomUserView(generics.CreateAPIView, generics.ListAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer

    def get(self, request, *args, **kwargs):
        if request.query_params.get('telegram_id'):
            try:
                queryset = CustomUser.objects.get(telegram_id=request.query_params['telegram_id'])
                user = model_to_dict(queryset)
                return Response({'error': False, 'detail': [], 'queryset': user})
            except Exception as ex:
                return Response({'error': True, 'detail': ex.args[0], 'queryset': {}}, status=status.HTTP_404_NOT_FOUND)
        return self.list(request, *args, **kwargs)


class ItemView(generics.CreateAPIView, generics.ListAPIView):
    queryset = ItemModel.objects.all()
    serializer_class = ItemSerializer

    def get(self, request, *args, **kwargs):
        if request.query_params.get('category'):
            category = request.query_params['category']
            response, category_id = self.get_category_id(category)
            if not response:
                return Response({'error': True, 'detail': category_id, 'queryset': None}, status=status.HTTP_404_NOT_FOUND)

            if not request.query_params.get('next_id_for') and not request.query_params.get('previous_id_before'):
                queryset = ItemModel.objects.filter(category=category_id)
                if queryset:
                    serializer = self.get_serializer(queryset, many=True)
                    amount = self.get_amount_in_category(category_id)
                    return Response({"amount": amount, "queryset": serializer.data})
                else:
                    return Response({'error': True, 'detail': "Ничего не нашлось по вашему запросу", 'queryset': None}, status=status.HTTP_404_NOT_FOUND)

            elif request.query_params.get('next_id_for'):
                if request.query_params['next_id_for'] == '0':
                    queryset = ItemModel.objects.filter(category=category_id).first()
                    if queryset:
                        amount = self.get_amount_in_category(category_id)
                        serializer = self.get_serializer(queryset)
                        return Response({"amount": amount, "queryset": serializer.data})
                    else:
                        return Response({"error": True, "detail": "Ничего не нашлось по вашему запросу", "queryset": []}, status=status.HTTP_404_NOT_FOUND)

                else:
                    queryset = ItemModel.objects.filter(category=category_id, id__gt=request.query_params['next_id_for']).first()
                    if queryset:
                        amount = self.get_amount_in_category(category_id)
                        serializer = self.get_serializer(queryset)
                        return Response({"amount": amount, "queryset": serializer.data})
                    else:
                        return Response({"error": True, "detail": "Ничего не нашлось по вашему запросу", "queryset": []}, status=status.HTTP_404_NOT_FOUND)

            elif request.query_params.get('previous_id_before'):
                if request.query_params['previous_id_before'] == '0':
                    queryset = ItemModel.objects.filter(category=category_id).last()
                else:
                    queryset = ItemModel.objects.filter(category=category_id, id__lt=request.query_params['previous_id_before']).last()
                if queryset:
                    amount = self.get_amount_in_category(category_id)
                    serializer = self.get_serializer(queryset)
                    return Response({"amount": amount, "queryset": serializer.data})
                else:
                    return Response({"error": True, "detail": "Ничего не нашлось по вашему запросу", "queryset": []}, status=status.HTTP_404_NOT_FOUND)
        elif request.query_params.get('id'):
            try:
                id = request.query_params['id']
                queryset = ItemModel.objects.get(id=id)
                serializer = model_to_dict(queryset)
                return Response(serializer)
            except Exception as ex:
                print(ex)
                return Response([], status=status.HTTP_404_NOT_FOUND)

        return self.list(request, *args, **kwargs)

    def get_amount_in_category(self, category_id):
        return ItemModel.objects.filter(category=category_id).count()

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"amount": len(serializer.data), "queryset": serializer.data})

    def get_category_id(self, category)-> [bool, int]:
        try:
            return True, CategoriesModel.objects.get(name=category).id
        except Exception as ex:
            return False, ex.args[0]

class CategoryView(generics.CreateAPIView, generics.ListAPIView):
    queryset = CategoriesModel.objects.all()
    serializer_class = CategoriesSerializer

    def get(self, request, *args, **kwargs):
        if request.query_params.get('name'):
            try:
                response = CategoriesModel.objects.get(name=request.query_params['name'])
                return Response({'error': False, 'detail': None, 'queryset': model_to_dict(response)})
                pass
            except Exception as ex:
                print(ex)
                return Response({'error': True, 'detail': ex.args[0], 'queryset': None})
        return self.list(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        # super().list(request, *args, **kwargs)
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({"error": False, "detail": None, "queryset": serializer.data})

class ShoppingCartView(generics.CreateAPIView, generics.ListAPIView, generics.UpdateAPIView, generics.DestroyAPIView):
    queryset = ShoppingCartModel.objects.all()
    serializer_class = ShoppingCartSerializer

    def get(self, request, *args, **kwargs):
        user = request.query_params['user'] if request.query_params.get('user') else None
        item = request.query_params['item'] if request.query_params.get('item') else None

        if user and item:
            queryset = ShoppingCartModel.objects.filter(user=user, item=item)
        elif user and not item:
            queryset = ShoppingCartModel.objects.filter(user=user)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

