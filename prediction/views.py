from django.shortcuts import render, redirect, get_object_or_404
import joblib
import os
import requests
from django.contrib.auth import authenticate, login, logout
from prediction.forms import RegisterForm, LoginForm
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from .models import Diamond, DiamondPrediction, CartItem, Order, OrderItem
from .forms import DiamondForm
from django.core.paginator import Paginator



#USD to IDR Converter
def get_usd_to_idr_rate():
    try:
        api_key = 'f772561127813cd5ad285d3a'
        url = f"https://v6.exchangerate-api.com/v6/{api_key}/latest/USD"
        response = requests.get(url, timeout=5)
        data = response.json()
        return data["conversion_rates"]["IDR"]
    except Exception as e:
        print(f"Exchange Rate Error: {e}")
        return 16000  # fallback
    
# Get current directory
current_dir = os.path.dirname(__file__)

# Load model package
model_path = os.path.join(current_dir, 'diamond_price_predictor_full.pkl')
package = joblib.load(model_path)

model = package['model']
preprocessor = package['preprocessor']
features_used = package['features']

def home(request):
    diamonds = Diamond.objects.all()
    return render(request, 'home.html', {'diamonds':diamonds})

def predict_price(request):
    if request.method == 'POST':
        try:
            # Get all form values
            carat = float(request.POST.get('carat'))
            depth = float(request.POST.get('depth'))
            table = float(request.POST.get('table'))
            x = float(request.POST.get('x'))
            y = float(request.POST.get('y'))
            z = float(request.POST.get('z'))
            cut_label = int(request.POST.get('cut_label'))
            clarity_label = int(request.POST.get('clarity_label'))
            color_index = int(request.POST.get('color_index'))

            cut = request.POST.get('cut')
            clarity = request.POST.get('clarity')
            color = request.POST.get('color')

            # One-hot encode color
            color_features = [0] * 7
            color_features[color_index] = 1

            # Final input in the correct order
            final_input = [carat, depth, table, x, y, z] + color_features + [cut_label, clarity_label]

            # Predict USD price
            predicted_price_usd = model.predict([final_input])[0]
            predicted_price_usd = round(predicted_price_usd, 2)

            # Convert to IDR
            rate = get_usd_to_idr_rate()
            if rate is None:
                raise Exception("Failed to fetch exchange rate.")
            predicted_price_idr = round(predicted_price_usd * rate, 2)

            # ✅ Save to DiamondPrediction table
            DiamondPrediction.objects.create(
                carat=carat,
                cut=cut,
                color=color,
                clarity=clarity,
                depth=depth,
                table=table,
                x=x,
                y=y,
                z=z,
                predicted_price_usd=predicted_price_usd,
                predicted_price_idr=predicted_price_idr,
            )

            context = {
                'predicted_price': predicted_price_usd,
                'predicted_price_idr': f"Rp {predicted_price_idr:,.2f}"
            }

            return render(request, 'predict.html', context)

        except Exception as e:
            return render(request, 'predict.html', {'error': f'Something went wrong: {e}'})

    return render(request, 'predict.html')


def information(request):
    return render(request, 'information.html')

def product(request):
    diamonds = Diamond.objects.all()
    paginator = Paginator(diamonds, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'product.html', {'page_obj':page_obj})

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already in use.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password)
        messages.success(request, "Account created successfully! You can now log in.")
        return redirect('login')

    return render(request, 'register.html')

def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        
        # Look up the user by email
        from django.contrib.auth.models import User
        try:
            username = User.objects.get(email=email).username
        except User.DoesNotExist:
            messages.error(request, "Invalid credentials")
            return redirect('login')
        
        # Authenticate by username (not email)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Change to your homepage
        else:
            messages.error(request, "Invalid credentials")
            return redirect('login')
    
    return render(request, 'login.html')
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def add_to_cart(request, diamond_id):
    diamond = get_object_or_404(Diamond, id=diamond_id)
    cart_item, created = CartItem.objects.get_or_create(user=request.user, diamond=diamond)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.diamond.price_idr * item.quantity for item in cart_items)
    return render(request, 'cart/view_cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, user=request.user)
    cart_item.delete()
    return redirect('view_cart')

@staff_member_required(login_url='login')
def admin_dashboard(request):
    # CRUD Product logic
    return render(request, 'dashboard.html')

def admin_only(user):
    return user.is_superuser

@login_required
@user_passes_test(admin_only)
def diamond_list(request):
    diamonds = Diamond.objects.all().order_by('-id')
    paginator = Paginator(diamonds, 10)  # Show 10 diamonds per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'diamond/diamond_list.html', {'page_obj': page_obj})

@login_required
@user_passes_test(admin_only)
def diamond_create(request):
    if request.method == 'POST':
        form = DiamondForm(request.POST, request.FILES)  # Add request.FILES here
        if form.is_valid():
            form.save()
            return redirect('diamond_list')
    else:
        form = DiamondForm()
    return render(request, 'diamond/diamond_form.html', {'form': form, 'title': 'Add Diamond'})

@login_required
@user_passes_test(admin_only)
def diamond_update(request, pk):
    diamond = get_object_or_404(Diamond, pk=pk)
    if request.method == 'POST':
        form = DiamondForm(request.POST, request.FILES, instance=diamond)
        if form.is_valid():
            form.save()
            return redirect('diamond_list')
    else:
        form = DiamondForm(instance=diamond)
    return render(request, 'diamond/diamond_form.html', {'form': form, 'title': 'Edit Diamond'})

@login_required
@user_passes_test(admin_only)
def diamond_delete(request, pk):
    diamond = get_object_or_404(Diamond, pk=pk)
    if request.method == 'POST':
        diamond.delete()
        return redirect('diamond_list')
    return render(request, 'diamond/diamond_confirm_delete.html', {'diamond': diamond})

def is_admin(user):
    return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def prediction_history_view(request):
    predictions = DiamondPrediction.objects.all().order_by('-created_at')
    paginator = Paginator(predictions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'prediction_history.html', {'page_obj': page_obj})

@login_required
def checkout(request):
    cart_items = CartItem.objects.filter(user=request.user)

    #Prevent access to checkout if cart is empty
    if not cart_items.exists():
        return redirect('view_cart')  # Redirect back to the cart page
    
    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        total_price = sum(item.diamond.price_idr * item.quantity for item in cart_items)

        # Save order
        order = Order.objects.create(user=request.user, full_name=name, address=address, total_price=total_price)
        for item in cart_items:
            OrderItem.objects.create(order=order, diamond=item.diamond, quantity=item.quantity)
        cart_items.delete()  # Clear cart

        return render(request, 'cart/checkout_success.html', {'order': order})

    return render(request, 'cart/checkout.html', {'cart_items': cart_items})

@login_required
@user_passes_test(is_admin)
def order_list(request):
    orders = Order.objects.all().order_by('-created_at')
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'order_list.html',  {'page_obj': page_obj})
