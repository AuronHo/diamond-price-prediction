from django.urls import path
from . import views
from prediction.views import home, predict_price, information, product
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),
    path('predict/', predict_price, name='predict_price'),
    path('information/', information, name='information'),
    path('product/', product, name='product'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.admin_dashboard, name='dashboard'),

    # Diamond Products CRUD paths
    path('dashboard/diamonds/', views.diamond_list, name='diamond_list'),
    path('dashboard/diamonds/add/', views.diamond_create, name='diamond_create'),
    path('dashboard/diamonds/edit/<int:pk>/', views.diamond_update, name='diamond_update'),
    path('dashboard/diamonds/delete/<int:pk>/', views.diamond_delete, name='diamond_delete'),

    #Prediction History
    path('dashboard/predictions/', views.prediction_history_view, name='prediction-history'),

    #Cart Functions
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:diamond_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),

    #Order List
    path('orders/', views.order_list, name='order_list'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)