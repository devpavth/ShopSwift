from django.shortcuts import render,redirect,get_object_or_404
from django.http import JsonResponse
import json
import datetime

# for login form
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm, ReviewForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

# for paypal integration
from django.urls import reverse
import stripe
from django.conf import settings
# from django.views.decorators.csrf import csrf_exempt

from .models import *
from .utils import cookieCart, cartData, guestOrder
from django.db.models import Sum

# Create your views here.

def store(request):
    data = cartData(request)  
    cartItems = data['cartItems']

    products = Product.objects.all()
    context={'products':products, 'cartItems': cartItems}
    return render(request,'store/store.html',context)

def cart(request):
    data = cartData(request)
    print('data:',data)
    
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']


    context={'items' : items, 'order' : order, 'cartItems': cartItems} 
    return render(request,'store/cart.html',context)

def checkout(request):
    if request.method == 'POST':
        stripe.api_key = settings.STRIPE_SECRET_KEY
        YOUR_DOMAIN = 'http://127.0.0.1:8000'

        cart_info = cartData(request)
        order = cart_info['order']

        if isinstance(order, dict):
            cart_total_price = order.get('get_cart_total', 0)
        else:
            cart_total_price = order.get_cart_total

        user_location = determine_user_location(request)
        address = get_address_for_location(user_location)

        customer = stripe.Customer.create(
            name="Pavi",
            address=address,
        )
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price_data': {
                        'currency': 'inr',  # Replace with your currency code
                        'product_data': {
                            'name': 'Total Order Price',
                        },
                        'unit_amount': int(cart_total_price * 100),  # Convert to cents
                    },
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success',
            cancel_url=YOUR_DOMAIN + '/cancel',
            customer=customer.id,
            billing_address_collection='auto',
            shipping_address_collection={
                'allowed_countries': ['US']  # Replace 'US' with the appropriate country code
            },
        )
        return redirect(checkout_session.url, code=303)
    
    data = cartData(request)
    
    cartItems = data['cartItems']
    order = data['order']
    items = data['items']

    context={'items' : items, 'order' : order,'cartItems': cartItems}
    return render(request,'store/checkout.html',context)


def updateItem(request):
    data = json.loads(request.body)
    productId = data['productId']
    action = data['action']

    print('Action:',action)
    print('productId:',productId)

    customer  = request.user.customer
    product = Product.objects.get(id=productId)
    order, created  = Order.objects.get_or_create(customer=customer,complete = False)

    orderItem, created = OrderItem.objects.get_or_create(order=order,product=product)

    if action == 'add':
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()

    return JsonResponse('Item was added', safe=False)


def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer
        order, created  = Order.objects.get_or_create(customer=customer,complete = False)
        
    else:
        customer, order = guestOrder(request, data)

    total = float(data['form']['total'])
    print(f'Total: {total}')
    order.transaction_id = transaction_id

    if total == float(order.get_cart_total):
        print(f'Total: {total}, Cart Total: {order.get_cart_total}')
        order.complete = True
    order.save() 

    print('Order marked as complete')
    #request.session.pop('cart', None)

    if order.shipping == True:
        ShippingAddress.objects.create(
            customer = customer,
            order = order,
            address = data['shipping']['address'],
            area = data['shipping']['area'],
            city = data['shipping']['city'],
            state = data['shipping']['state'],
            pincode = data['shipping']['pincode'],
        )

    return JsonResponse('Payment complete!', safe=False)
    # else:
    #     print(f'Total mismatch - Total: {total}, Cart Total: {order.get_cart_total()}')
    #     return JsonResponse('Transaction failed', safe=False)



def registerPage(request):
    if request.user.is_authenticated:
        return redirect('store')
    else:
        form = CreateUserForm()

        if request.method == 'POST':
            form = CreateUserForm(request.POST)  
            if form.is_valid():
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password1'])
                user.save()
                messages.success(request, f"{user.username}, Account was created Successfully")
                return redirect('login')

        context = {'form': form}
        return render(request,'store/register.html',context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('store')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')

            #print('username:',username,'password:',password)

            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                customer, created = Customer.objects.get_or_create(user=user)
                return redirect('store')
            else:
                messages.error(request, 'Invalid username or password')

        context = {}
        return render(request,'store/login.html',context)

def logoutUser(request):
    if request.user.is_authenticated:
        logout(request)
    return redirect('store')

def productDetailsView(request,product_id):
    data = cartData(request)
    print('data:',data)
    
    cartItems = data['cartItems']
    total_quantity = OrderItem.objects.filter(order__isnull=False, product_id=product_id).aggregate(Sum('quantity'))['quantity__sum'] or 0
    print(f'Total Quantity: {total_quantity}')
    order = data['order']
    
    product = get_object_or_404(Product, pk=product_id)
    reviews = Review.objects.filter(product=product)
    some_debug_variable = "Debug info"
    context = {'product':product, 'cartItems': cartItems, 'total_quantity':total_quantity,'order': order,'reviews': reviews, 'some_debug_variable': some_debug_variable}
    return render(request,'store/product-details.html',context)


def reviewPage(request,product_id):
    product = get_object_or_404(Product, pk=product_id)
    data = cartData(request)
    cartItems = data['cartItems']
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('product_details', product_id = product_id)
    else:
        form = ReviewForm()

    context = {'form':form, 'product': product, 'cartItems': cartItems}
    return render(request,'store/review-page.html',context)




# def charge(request):
#     amount = 5
#     if request.method == 'POST':
#         print('Data:',request.POST)
    
#     return redirect(reverse('success',args=[amount]))

def successMsg(request):
    return render(request, 'store/success.html')

    # return redirect('store')

def payment_cancelled(request):
    return render(request, 'store/cancel.html')
    #return redirect('store')


def determine_user_location(request):
    return 'IN'

def get_address_for_location(user_location):
    if user_location == 'IN':
        # For users in India, provide an Indian address
        return {
            "line1": "123 International Street",
            "postal_code": "54321",
            "city": "International City",
            "state": "International State",
            "country": "US",  # Update this with the appropriate country code
        }
    else:
        # For users outside India, provide an address outside India
        return {
            "line1": "13 Main Street",
            "postal_code": "12345",
            "city": "City",
            "state": "State",
            "country": user_location,  # Use the user's location as the country code
        }