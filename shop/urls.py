from django.urls import path
from . import views

app_name = "shop"

urlpatterns = [
    # Main Pages
    path('', views.home, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),

    # Cart
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:product_id>/', views.update_cart, name='update_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Checkout & Razorpay
    path('checkout/', views.checkout_view, name='checkout'),
    path('payment/verify/', views.payment_verify, name='payment_verify'),
    path('payment/success/<int:order_id>/', views.payment_success, name='payment_success'),
    path('payment/failed/', views.payment_failed, name='payment_failed'),

    # User Auth
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    path('profile/', views.profile_view, name='profile'),

    # Product Detail
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),

    # Static Pages
    path('page/<slug:slug>/', views.static_page_view, name='static_page'),
    path('privacy/', views.static_page_view, {'slug': 'privacy'}, name='privacy'),
    path('terms/', views.static_page_view, {'slug': 'terms'}, name='terms'),
]
