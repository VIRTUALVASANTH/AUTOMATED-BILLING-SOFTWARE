import json
from django.db.models.fields import DecimalField
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import *
from django.http import JsonResponse
from .utils import cartData

def mainpage(request):
    '''
    For logging users in
    '''
    if request.method == "POST":
        type = request.POST.get('type')
        if type=="login":
            username = request.POST.get('username')
            password = request.POST.get('password')
            user=authenticate(request,username=username,password=password)  #django default authentication
            if user is not None:
                login(request,user)
                return redirect('customerhomepage')
            else: 
                messages.error(request,"Wrong Credentials! Please Try again")
        elif type=="register":
            username = request.POST.get('username')
            email = request.POST.get('email')
            password = request.POST.get('password')
            try:   #creating Customer object
                user=CustomUser.objects.create_user(username=username,password=password,email=email,user_type=3)
                user.customer.name=username #adding name to instructor object
                user.save()
                messages.success(request," Signup successfull ")
                return redirect('loginpage')
            except:
                messages.error(request," Error occured. Please Try again!")
                return redirect('loginpage')
    return render(request, 'login.html')   


def dashboard(request):
    if (request.user.is_authenticated)==False:
        return redirect('loginpage')

    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'cartItems':cartItems}
    return render(request, 'index.html', context)   

def logoutuser(request):
    '''
    for logging user out and redirecting to login-page
    '''
    logout(request)
    return redirect('loginpage')

def scanner(request):
    if (request.user.is_authenticated)==False:
        return redirect('loginpage')

    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'cartItems':cartItems}
    return render(request,'scanner.html', context)

def cart(request):
    if (request.user.is_authenticated)==False:
        return redirect('loginpage')

    data = cartData(request)

    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context = {'cartItems':cartItems, 'order':order, 'items':items}
    return render(request,'cart.html', context)


def addtocart(request):
    product = request.GET.get('productid', None)
    action = request.GET.get('action')
    data = {
        'added': Product.objects.filter(id=product).exists()
    }
    if (Product.objects.filter(id=product).exists()):
        customer = request.user.customer
        product = Product.objects.get(id=product)
        order, created = Order.objects.get_or_create(customer=customer, complete=False)
        orderItem, created = OrderItem.objects.get_or_create(order=order, product=product)

        if action == 'add':
            orderItem.quantity = (orderItem.quantity + 1)
        elif action == 'remove':
            orderItem.quantity = (orderItem.quantity - 1)

        orderItem.save()
        if orderItem.quantity <= 0:
            orderItem.delete()

    return JsonResponse(data)


def checkout(request):
    if (request.user.is_authenticated)==False:
        return redirect('loginpage')
    data = cartData(request)
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    order.complete = True
    order.save()
    orderid = order.id
    context = {'cartItems':cartItems, 'order':order, 'items':items, 'orderid': orderid}
    return render(request, 'checkout.html', context)


def loginGuard(request):
    '''
    For logging users in
    '''
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        user=authenticate(request,username=username,password=password)  #django default authentication
        if user is not None:
            login(request,user)
            if user.user_type=='2' or user.user_type=='1':
                return redirect('guardHome')
            else:
                messages.error(request," Wrong Credentials! Please Try again or contact your administrator")
        else:
            messages.info(request," Wrong Credentials! Please Try again or contact your administrator")

    return render(request,'guard/login.html')

def scanGuard(request):
    if (request.user.is_authenticated)==False:
        return redirect('guardlogin')

    return render(request,'guard/scanner.html')


def getdetailsGuard(request):
    orderid = request.GET.get('orderid', None)
    data = {
        'added': Order.objects.filter(id=orderid).exists()
    }
    if (Order.objects.filter(id=orderid).exists()):
        request.session['currentOrder'] = orderid
    return JsonResponse(data)


def verifyGuard(request):
    if (request.user.is_authenticated)==False:
        return redirect('guardlogin')

    orderid = request.session['currentOrder']
    order = Order.objects.get(id=orderid)
    if order==None:
        return redirect('guardHome')
    else:
        customer = order.customer
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items

    context =  {'cartItems':cartItems ,'order':order, 'items':items}
    return render(request, 'guard/verify.html', context)

def logoutGuard(request):
    logout(request)
    return redirect('guardlogin')

def verified(request):
    if request.method=='GET':
        orderid = request.GET.get('order')
        orderid = int(orderid)
        order = Order.objects.get(id=orderid)
        order.verified = True
        order.save()
        del request.session['currentOrder']
    return redirect('guardHome')

def raiseIssue(request):
    if request.method=='GET':
        orderid = request.GET.get('order')
        orderid = int(orderid)
        order = Order.objects.get(id=orderid)
        order.issueRaised = True
        order.save()
        del request.session['currentOrder']
    return redirect('guardHome')

from django.shortcuts import render

def payment_confirmation(request):
    return render(request, 'payment_confirmation.html')


from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from.models import OrderItem, Product
from.utils import update_cart_total

@login_required
def update_item(request, product_id):
    product = Product.objects.get(id=product_id)
    order_item, created = OrderItem.objects.get_or_create(product=product, user=request.user)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity'))
        if quantity > 0:
            order_item.quantity = quantity
            order_item.save()
            update_cart_total(request.user)
            return redirect('cart')
        else:
            order_item.delete()
            return redirect('cart')
    return redirect('cart')


from django.shortcuts import redirect, get_object_or_404
from.models import OrderItem
from.utils import remove_from_cart

def remove_item(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    remove_from_cart(request.user, product)
    return redirect('cart')

# Ensure you have imported these lines
from .models import *
from .forms import CheckoutForm

from django.shortcuts import render, redirect
from django.conf import settings
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from .models import Order
from .forms import CheckoutForm
from django.views.decorators.csrf import csrf_exempt

import json
from django.db.models.fields import DecimalField
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import *
from django.http import JsonResponse
from .utils import cartData

# Other imports remain unchanged...

import requests

def shorten_url(url):
    # TinyURL endpoint for creating short URLs
    api_url = 'http://tinyurl.com/api-create.php?url=' + url
    response = requests.get(api_url)
    return response.text.strip()  # Strip any extra whitespace or newline characters

def send_payment_link(request):
    if request.method == 'POST':
        phone_number = request.POST['contact']
        total_amount = request.user.customer.order_set.filter(complete=False).first().get_cart_total

        # Ensure phone number is in E.164 format
        if not phone_number.startswith('+'):
            phone_number = '+91' + phone_number

        # UPI payment link
        upi_link = f"upi://pay?pa=suhasjayanth4@oksbi&pn=SUHASR&am={total_amount:.2f}&cu=INR&aid=uGICAgIC19YXhHw"

        # Shorten UPI link using TinyURL
        shortened_url = shorten_url(upi_link)

        # SMS message body with shortened URL
        message_body = f"Please complete your payment. Click this link to pay: {shortened_url}"

        # Twilio SMS sending
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        try:
            message = client.messages.create(
                body=message_body,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone_number
            )
            return render(request, 'payment_confirmation.html')
        except TwilioRestException as e:
            return render(request, 'cart.html', {'error': str(e)})

    return redirect('cart')


def checkout(request):
    customer = request.user.customer
    order, created = Order.objects.get_or_create(customer=customer, complete=False)
    items = order.orderitem_set.all()
    cartItems = order.get_cart_items

    form = CheckoutForm()

    context = {'items': items, 'order': order, 'cartItems': cartItems, 'form': form}
    return render(request, 'checkout.html', context)

@csrf_exempt
def process_checkout(request):
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            email_or_phone = form.cleaned_data['email_or_phone']
            # Implement payment processing logic here
            return render(request, 'payment_confirmation.html')

    return redirect('checkout')
