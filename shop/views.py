from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
from django.conf import settings
from datetime import datetime
import razorpay

from .models import Product, Category, About, Cart, CartItem, StaticPage, Order, OrderItem, UserPurchaseHistory
from .forms import ContactForm ,UserLoginForm,User,UserSignupForm
from festival.models import FestivalSale

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# ---------------- MAIN PAGES ---------------- #
def home(request):
    current_time = timezone.now()
    sale = FestivalSale.objects.filter(start_date__lte=current_time, end_date__gte=current_time, is_active=True).first()
    categories = Category.objects.all()
    category_products = {category: category.products.all() for category in categories}

    context = {
        'sale': sale,
        'button_text': "Shop Now",
        'festival_option': "Check out our Festival Sale Options",
        'category_products': category_products,
        'title': "Home",
        'now': datetime.now(),
    }
    return render(request, 'shop/index.html', context)


def about_view(request):
    about = About.objects.order_by("-updated_at").first()
    return render(request, "shop/about.html", {"about": about, "now": timezone.now()})


def contact_view(request):
    success = False
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            success = True
            form = ContactForm()
    else:
        form = ContactForm()
    return render(request, 'shop/contact.html', {'form': form, 'success': success, 'now': datetime.now()})


# ---------------- SIGNUP ----------------
def register_view(request):
    if request.user.is_authenticated:
        return redirect('shop:profile')

    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully!")
            return redirect('shop:profile')
    else:
        form = UserSignupForm()

    context = {
        'form': form,
        'now': datetime.now()
    }
    return render(request, 'shop/register.html', context)


# ---------------- LOGIN ----------------
def login_view(request):
    if request.user.is_authenticated:
        return redirect('shop:profile')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            login_input = form.cleaned_data['login']
            password = form.cleaned_data['password']

            # Authenticate using username or email
            user = authenticate(request, username=login_input, password=password)
            if user is None:
                # Try email if username didn't work
                try:
                    user_obj = User.objects.get(email=login_input)
                    user = authenticate(request, username=user_obj.username, password=password)
                except User.DoesNotExist:
                    user = None

            if user:
                login(request, user)
                messages.success(request, "Logged in successfully!")
                return redirect('shop:profile')
            else:
                messages.error(request, "Invalid credentials")

    else:
        form = UserLoginForm()

    context = {
        'form': form,
        'now': datetime.now()
    }
    return render(request, 'shop/login.html', context)


# ---------------- LOGOUT ----------------
def logout_view(request):
    logout(request)
    messages.success(request, "You have logged out successfully.")
    return redirect('shop:login')


# ---------------- USER PROFILE ----------------
@login_required(login_url='/login/')
def profile_view(request):
    context = {
        'user_obj': request.user,
        'now': datetime.now()
    }
    return render(request, 'shop/profile.html', context)


# ---------------- CART SYSTEM ---------------- #
def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            cart = Cart.objects.filter(id=cart_id).first()
            if not cart:
                cart = Cart.objects.create()
                request.session['cart_id'] = cart.id
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    return cart


def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
    cart_item.save()
    messages.success(request, f'Added {product.name} to cart!')
    return redirect('shop:cart')


def cart_view(request):
    cart = get_or_create_cart(request)
    return render(request, 'shop/cart.html', {'items': cart.items.all(), 'cart': cart, 'now': datetime.now()})


def update_cart(request, product_id):
    cart = get_or_create_cart(request)
    product = get_object_or_404(Product, id=product_id)
    quantity = int(request.POST.get('quantity', 0))
    if quantity > 0:
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        cart_item.quantity = quantity
        cart_item.save()
    else:
        CartItem.objects.filter(cart=cart, product=product).delete()
    return redirect('shop:cart')


def remove_from_cart(request, product_id):
    cart = get_or_create_cart(request)
    CartItem.objects.filter(cart=cart, product_id=product_id).delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('shop:cart')


# ---------------- PRODUCT DETAIL ---------------- #
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    return render(request, 'shop/productview.html', {'product': product, 'now': datetime.now()})


# ---------------- STATIC PAGES ---------------- #
def static_page_view(request, slug):
    page = get_object_or_404(StaticPage, slug=slug)
    if page.external_url:
        return redirect(page.external_url)
    return render(request, 'shop/static_page.html', {'page': page, 'now': datetime.now()})


# ---------------- CHECKOUT & PAYMENT ---------------- #
# ---------------- CHECKOUT & PAYMENT ---------------- #
@login_required
def checkout_view(request):
    cart = get_or_create_cart(request)
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty')
        return redirect('shop:cart')

    if request.method == 'POST':
        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        city = request.POST.get('city')
        address = request.POST.get('address')
        pincode = request.POST.get('pincode')

        if not all([name, mobile, city, address, pincode]):
            messages.error(request, 'All fields are required!')
            return redirect('shop:checkout')

        from decimal import Decimal
        amount = int(Decimal(cart.total) * 100)  # Convert to paise

        # Create Razorpay order
        try:
            razorpay_order = razorpay_client.order.create({
                'amount': amount,
                'currency': 'INR',
                'payment_capture': '1'
            })
        except Exception as e:
            messages.error(request, f'Failed to create payment order: {str(e)}')
            return redirect('shop:checkout')

        # Save order
        order = Order.objects.create(
            user=request.user,
            name=name,
            mobile=mobile,
            city=city,
            address=address,
            pincode=pincode,
            amount=cart.total,
            razorpay_order_id=razorpay_order['id'],
            status="Pending"
        )

        # Create order items
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.name,
                quantity=item.quantity,
                price=item.product.price
            )

        context = {
            'cart': cart,
            'order': order,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'amount': amount,
            'currency': 'INR',
            'show_payment': True,  # This flag shows payment section
            'user_name': request.user.get_full_name() or request.user.username,
            'user_email': request.user.email,
            'user_mobile': mobile,
            'now': timezone.now()
        }
        return render(request, 'shop/checkout.html', context)

    # GET request - show delivery form
    context = {
        'cart': cart,
        'show_payment': False,
        'now': timezone.now()
    }
    return render(request, 'shop/checkout.html', context)


# ---------------- PAYMENT VERIFY ---------------- #
@csrf_exempt
def payment_verify(request):
    if request.method == "POST":
        data = request.POST
        try:
            razorpay_order_id = data.get('razorpay_order_id')
            razorpay_payment_id = data.get('razorpay_payment_id')
            razorpay_signature = data.get('razorpay_signature')

            if not all([razorpay_order_id, razorpay_payment_id, razorpay_signature]):
                messages.error(request, "Invalid payment data received")
                return redirect('shop:payment_failed')

            order = Order.objects.get(razorpay_order_id=razorpay_order_id)

            # Verify signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': razorpay_payment_id,
                'razorpay_signature': razorpay_signature
            }
            
            razorpay_client.utility.verify_payment_signature(params_dict)

            # Payment verified successfully
            order.razorpay_payment_id = razorpay_payment_id
            order.razorpay_signature = razorpay_signature
            order.status = "Paid"
            order.save()

            # Save purchase history
            for item in order.items.all():
                UserPurchaseHistory.objects.create(
                    user=order.user,
                    product=item.product,
                    order=order,
                    quantity=item.quantity
                )

            # Clear cart
            if request.user.is_authenticated:
                Cart.objects.filter(user=request.user).delete()
            else:
                # Clear session cart
                cart_id = request.session.get('cart_id')
                if cart_id:
                    Cart.objects.filter(id=cart_id).delete()
                    del request.session['cart_id']

            messages.success(request, "Payment successful! Your order has been placed.")
            return redirect('shop:payment_success', order_id=order.id)

        except Order.DoesNotExist:
            messages.error(request, "Order not found")
            return redirect('shop:payment_failed')
        except razorpay.errors.SignatureVerificationError:
            messages.error(request, "Payment signature verification failed")
            return redirect('shop:payment_failed')
        except Exception as e:
            print(f"Payment verification error: {str(e)}")
            messages.error(request, "Payment verification failed. Please contact support.")
            return redirect('shop:payment_failed')

    return HttpResponseBadRequest("Invalid request method")


@login_required
def payment_success(request, order_id=None):
    order = None
    if order_id:
        order = get_object_or_404(Order, id=order_id, user=request.user)
    context = {
        'order': order,
        'now': timezone.now()
    }
    return render(request, 'shop/payment_success.html', context)


@login_required
def payment_failed(request):
    context = {
        'now': timezone.now()
    }
    return render(request, 'shop/payment_failed.html', context)
