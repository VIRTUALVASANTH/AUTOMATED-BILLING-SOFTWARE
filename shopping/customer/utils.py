import json
from .models import *


def cartData(request):
	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
		items = order.orderitem_set.all()
		cartItems = order.get_cart_items
	else:
		cartItems = {}
		order = {}
		items = {}

	return {'cartItems':cartItems ,'order':order, 'items':items}


# utils.py

from decimal import Decimal
from django.db.models import Sum
from django.contrib.auth.models import User
from .models import OrderItem, Product

def update_cart_total(user):
    """
    Updates the total cost of the cart for the given user.
    """
    order_items = OrderItem.objects.filter(user=user)
    total = order_items.aggregate(total=Sum('product__price' * 'quantity'))['total']
    if total is None:
        total = Decimal(0.00)
    return total

def get_cart_items(user):
    """
    Returns a list of OrderItem instances in the cart for the given user.
    """
    return OrderItem.objects.filter(user=user)

def add_to_cart(user, product, quantity=1):
    """
    Adds a product to the cart for the given user.
    """
    order_item, created = OrderItem.objects.get_or_create(user=user, product=product)
    order_item.quantity += quantity
    order_item.save()

def remove_from_cart(user, product):
    """
    Removes a product from the cart for the given user.
    """
    OrderItem.objects.filter(user=user, product=product).delete()

def update_cart_item(user, product, quantity):
    """
    Updates the quantity of a product in the cart for the given user.
    """
    order_item = OrderItem.objects.get(user=user, product=product)
    order_item.quantity = quantity
    order_item.save()

def get_product_price(product_id):
    """
    Returns the price of a product by ID.
    """
    product = Product.objects.get(id=product_id)
    return product.price

def get_order_item_total(order_item):
    """
    Returns the total cost of an OrderItem instance.
    """
    return order_item.product.price * order_item.quantity