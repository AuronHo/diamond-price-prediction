from django.db import models

class Diamond(models.Model):
    CUT_CHOICES = [
        ('Fair', 'Fair'),
        ('Good', 'Good'),
        ('Very Good', 'Very Good'),
        ('Premium', 'Premium'),
        ('Ideal', 'Ideal'),
    ]

    CLARITY_CHOICES = [
        ('I1', 'I1 (Inclusions Included)'),
        ('SI2', 'SI2 (Slightly Included)'),
        ('SI1', 'SI1'),
        ('VS2', 'VS2 (Very Slightly Included)'),
        ('VS1', 'VS1'),
        ('VVS2', 'VVS2 (Very, Very Slightly Included)'),
        ('VVS1', 'VVS1'),
        ('IF', 'IF (Internally Flawless)'),
    ]

    COLOR_CHOICES = [
        ('D', 'D (Clear)'),
        ('E', 'E'),
        ('F', 'F'),
        ('G', 'G'),
        ('H', 'H'),
        ('I', 'I'),
        ('J', 'J (Yellowish)'),
    ]

    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='images/')  # or models.ImageField(upload_to='diamonds/') if using local media
    carat = models.DecimalField(max_digits=5, decimal_places=2)
    cut = models.CharField(max_length=50, choices=CUT_CHOICES)
    color = models.CharField(max_length=10, choices=COLOR_CHOICES)
    clarity = models.CharField(max_length=10, choices=CLARITY_CHOICES)
    depth = models.DecimalField(max_digits=5, decimal_places=2)
    table = models.DecimalField(max_digits=5, decimal_places=2)
    x = models.DecimalField(max_digits=5, decimal_places=2)  # length in mm
    y = models.DecimalField(max_digits=5, decimal_places=2)  # width in mm
    z = models.DecimalField(max_digits=5, decimal_places=2)  # depth in mm
    price_idr = models.BigIntegerField()

    def __str__(self):
        return f"{self.name} - {self.carat}ct - {self.cut}"
    
class DiamondPrediction(models.Model):
    carat = models.DecimalField(max_digits=5, decimal_places=2)
    cut = models.CharField(max_length=50)
    color = models.CharField(max_length=10)
    clarity = models.CharField(max_length=10)
    depth = models.DecimalField(max_digits=5, decimal_places=2)
    table = models.DecimalField(max_digits=5, decimal_places=2)
    x = models.DecimalField(max_digits=5, decimal_places=2)
    y = models.DecimalField(max_digits=5, decimal_places=2)
    z = models.DecimalField(max_digits=5, decimal_places=2)
    predicted_price_usd = models.DecimalField(max_digits=10, decimal_places=2)
    predicted_price_idr = models.BigIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Prediction on {self.created_at.date()} - ${self.predicted_price_usd}"
    
# models.py
from django.db import models
from django.contrib.auth.models import User
from .models import Diamond  # Assuming Diamond model already exists

class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    diamond = models.ForeignKey(Diamond, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.diamond.name} (x{self.quantity})"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    total_price = models.DecimalField(max_digits=12, decimal_places=2)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    diamond = models.ForeignKey(Diamond, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

