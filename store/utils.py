import json
from .models import *

def cookieCart(request):
    try:
        cart = json.loads(request.COOKIES['cart'])
        print('All Cookies:', request.COOKIES)
    except:
        cart = {}
        
    print('Cart:',cart)
    items = []
    order = {'get_cart_total' : 0, 'get_cart_items':0,'shipping':False}
    cartItems = 0

    if cart:
        for product_id, item_data in cart.items():
            try:
                print('Processing item:', product_id)
                cartItems += item_data['quantity']
                print('Current cartItems:', cartItems)

                product = Product.objects.get(id=product_id)
                print('Product:', product)

                total = (product.price * item_data['quantity'])

                order['get_cart_total'] += total
                order['get_cart_items'] += item_data['quantity']
                print('Current cartItems:', cartItems)

                item = {
                    'product':{
                        'id':product.id,
                        'name':product.name,
                        'price':product.price,
                        'imageURL':product.imageURL,
                        },
                    'quantity':item_data['quantity'],
                    'get_total':total,
                    }
                items.append(item)

                if product.digital == False:
                    order['shipping'] = True
            except Exception as e:
                print(f'Error processing item {product_id}: {e}')
    
    return {'cartItems': cartItems, 'order': order, 'items': items}


def cartData(request):
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created  = Order.objects.get_or_create(customer=customer,complete = False)
         
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items    
    else:
        cookieData = cookieCart(request)
        cartItems = cookieData['cartItems']
        order = cookieData['order']
        items = cookieData['items']
    return {'cartItems': cartItems, 'order': order, 'items': items}


def guestOrder(request,data):
    print('User is not logged in..')

    print('COOKIES:',request.COOKIES)
    name = data['form']['name']
    email = data['form']['email']

    cookieData = cookieCart(request)
    items = cookieData['items']

    customer, created = Customer.objects.get_or_create(
        email = email,
    )
    customer.name = name
    customer.save()

    order = Order.objects.create(
        customer = customer,
        complete = False,
    )

    for item in items:
        product = Product.objects.get(id=item['product']['id'])

        orderItem = OrderItem.objects.create(
            product=product,
            order = order,
            quantity = item['quantity']
        )
    return customer, order
