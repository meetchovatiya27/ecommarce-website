from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
from .models import Product, Category, About, Cart, CartItem, HomepageAnimation, StaticPage
from .forms import ContactForm, CustomUserCreationForm, CustomAuthenticationForm
from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from festival.models import FestivalSale
from django.utils.translation import gettext as _


def home(request):
    # Get active festival sale with DEBUG
    current_time = timezone.now()
    
    # Debug: Check all sales in database
    all_sales = FestivalSale.objects.all()
    print("=" * 50)
    print(f"DEBUG: Total sales in database: {all_sales.count()}")
    for s in all_sales:
        print(f"Sale ID: {s.id}")
        print(f"  Title: {s.title}")
        print(f"  Active: {s.is_active}")
        print(f"  Start: {s.start_date}")
        print(f"  End: {s.end_date}")
        print(f"  Is Ongoing: {s.is_ongoing()}")
        print("-" * 30)
    
    sale = FestivalSale.objects.filter(
        start_date__lte=current_time,
        end_date__gte=current_time,
        is_active=True
    ).first()
    
    print(f"Current time: {current_time}")
    print(f"Active sale found: {sale}")
    print("=" * 50)
    
    categories = Category.objects.all()
    category_products = {category: category.products.all() for category in categories}
    
    # Fetch homepage animation for aligning image and button animations
    animation = HomepageAnimation.objects.first()  # Adjust filter as needed

    context = {
        'sale': sale,
        'animation': animation,                         # New context for animation details
        'button_text': _("Shop Now"),                   # Translated button text
        'festival_option': _("Check out our Festival Sale Options"),  # Translated festival sale option
        'category_products': category_products,
        'title': _("Home"),
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

    return render(request, 'shop/contact.html', {
        'form': form,
        'success': success,
        'now': datetime.now()
    })


def login_view(request):
    if request.user.is_authenticated:
        return redirect("shop:profile")

    if request.method == "POST":
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("shop:home")
    else:
        form = CustomAuthenticationForm(request)
    return render(request, "shop/login.html", {"form": form, "now": datetime.now()})


def logout_view(request):
    logout(request)
    return redirect("shop:home")


def register_view(request):
    if request.user.is_authenticated:
        return redirect("shop:profile")

    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("shop:profile")
    else:
        form = CustomUserCreationForm()
    return render(request, "shop/register.html", {"form": form, "now": datetime.now()})


@login_required
def profile_view(request):
    return render(request, "shop/profile.html", {"user_obj": request.user, "now": datetime.now()})


# ---------------- CART SYSTEM ---------------- #

def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        cart_id = request.session.get('cart_id')
        if cart_id:
            try:
                cart = Cart.objects.get(pk=cart_id)
            except Cart.DoesNotExist:
                cart = Cart.objects.create()
                request.session['cart_id'] = cart.id
        else:
            cart = Cart.objects.create()
            request.session['cart_id'] = cart.id
    return cart


def add_to_cart(request, product_id):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=product_id)
        cart = get_or_create_cart(request)
        
        cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            cart_item.quantity += 1
        cart_item.save()
        
        messages.success(request, f'Added {product.name} to cart!')
        return redirect('shop:cart')
    
    return redirect('shop:home')


def cart_view(request):
    cart = get_or_create_cart(request)
    context = {
        'items': cart.items.all(),
        'total': cart.total,
        'now': datetime.now()
    }
    return render(request, 'shop/cart.html', context)


@login_required
def checkout_view(request):
    cart = get_or_create_cart(request)
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty')
        return redirect('shop:cart')
    
    context = {
        'cart': cart,
        'total': cart.total,
        'now': datetime.now()
    }
    return render(request, 'shop/checkout.html', context)


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
    if request.method == 'POST':
        cart = get_or_create_cart(request)
        CartItem.objects.filter(cart=cart, product_id=product_id).delete()
        messages.success(request, 'Item removed from cart.')
    return redirect('shop:cart')


# ---------------- PRODUCT DETAIL ---------------- #
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    context = {
        'product': product,
        'now': datetime.now()
    }
    return render(request, 'shop/productview.html', context)


# ---------------- STATIC PAGES (Privacy, Terms) ---------------- #
def static_page_view(request, slug):
    page = get_object_or_404(StaticPage, slug=slug)
    # If external URL is provided, redirect to it
    if page.external_url:
        return redirect(page.external_url)
    context = {
        'page': page,
        'now': datetime.now()
    }
    return render(request, 'shop/static_page.html', context)