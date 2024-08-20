from django.db import models

class CategoriesModel(models.Model):
    name = models.CharField(max_length=60, blank=False, null=False, unique=True)

    def __str__(self):
      return str(self.name)

class ItemModel(models.Model):
    name = models.CharField(max_length=100, blank=False, null=False)
    article = models.CharField(max_length=20, blank=False, null=False)
    manufactured = models.CharField(max_length=30, blank=True, null=True)
    size = models.CharField(max_length=15, blank=True, null=True)
    composition = models.CharField(max_length=100, blank=True, null=True)
    img_url = models.CharField(max_length=100, blank=False, null=False)
    site_card_item = models.CharField(max_length=100, blank=False, null=False)
    price = models.CharField(max_length=15, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    category = models.ForeignKey(CategoriesModel, on_delete=models.CASCADE)

    def __str__(self):
      return str(self.name)

class CustomUser(models.Model):
    telegram_id = models.CharField(max_length=15, blank=False, null=False, unique=True)
    username = models.CharField(max_length=50, blank=True, null=True)
    phone_number = models.CharField(max_length=50, blank=True, null=True)
    full_name = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(blank=False, null=False)

    def __str__(self):
      return str(self.telegram_id)

class Recycled(models.Model):
    item = models.ForeignKey(ItemModel, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
      return str(f"{self.user}->{self.item}")

class ShoppingCartModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    amount = models.IntegerField(auto_created=0)
    status = models.CharField(
        max_length=50,
        choices=[
            ('process', 'process'),
            ('confirmed_by_user', 'confirmed_by_user'),
            ('confirmed_by_sales_department', 'confirmed_by_sales_department'),
            ('goods shipped', 'goods shipped')
        ],
        default='process'
    )
    item = models.ForeignKey(ItemModel, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
      return str(f"{self.user}->{self.item}->{self.amount}")


