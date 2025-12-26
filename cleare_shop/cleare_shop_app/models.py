from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User



class Product(models.Model):
    SKIN_TYPE_CHOICES = [
        ('dry', 'Dry'),
        ('oily', 'Oily'),
        ('combination', 'Combination'),
        ('sensitive', 'Sensitive'),
        ('all', 'All skin types'),
    ]

    CATEGORY_CHOICES = [
        ('cleanser', 'Cleanser'),
        ('serum', 'Serum'),
        ('cream', 'Cream'),
        ('toner', 'Toner'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField()
    ingredients = models.TextField()
    usage = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    skin_type = models.CharField(max_length=20, choices=SKIN_TYPE_CHOICES)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    image = models.ImageField(upload_to='products/')
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Review(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.rating}/5"


class Order(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
    ]

    PAYMENT_CHOICES = [
        ('online', 'Online payment'),
        ('cod', 'Cash on delivery'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='processing')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} ({self.quantity})"


class Shipping(models.Model):
    DELIVERY_CHOICES = [
        ('standard', 'Standard delivery'),
        ('express', 'Express delivery'),
    ]

    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=30)
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_CHOICES)

    def __str__(self):
        return f"Shipping for Order #{self.order.id}"


class Promotion(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='promotions')
    discount_percent = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    start_date = models.DateTimeField(null=True, blank=True)
    end_date = models.DateTimeField(null=True, blank=True)

    def discounted_price(self):
        return self.product.price * (100 - self.discount_percent) / 100

    def __str__(self):
        return f"{self.product.name} - {self.discount_percent}%"

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('user', 'product')