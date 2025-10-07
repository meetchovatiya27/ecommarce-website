from .models import Cart

def cart_context(request):
    try:
        if request.user.is_authenticated:
            cart = Cart.objects.get(user=request.user)
        else:
            cart_id = request.session.get('cart_id')
            if cart_id:
                cart = Cart.objects.get(id=cart_id)
            else:
                return {'cart_item_count': 0}
        return {'cart_item_count': sum(item.quantity for item in cart.items.all())}
    except Cart.DoesNotExist:
        return {'cart_item_count': 0}
