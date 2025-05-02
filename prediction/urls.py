from django.urls import path
from . import views
from prediction.views import home, predict_price

urlpatterns = [
    path('', home, name='home'),
    path('predict/', predict_price, name='predict_price'),
]
