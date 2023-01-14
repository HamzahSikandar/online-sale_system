import imp
import json
from .models import *


def cookieCart(request):
    try:
        cart=json.loads(request.COOKIES['cart'])
    except:
            cart={}

    print('cart:',cart)
    items=[]
    order={'get_cart_total':5,'get_cart_items':0}
    cartItems=order['get_cart_items']
    for i in cart:

            try:

                cartItems += cart[i]['quantity']
                product=Product.objects.get(id=i)
                total=(product.price*cart[i]['quantity'])
                order['get_cart_total']+=total
                order['get_cart_items']+=cart[i]['quantity']
                item={
                    'product':{
                        'id':product.id,
                        'name':product.name,
                        'price':product.price,
                        'imageURL':product.imageURL,
                    },
                    'quantity':cart[i]['quantity'],
                    'get_total':total,
                }
                items.append(item)
                if product.digital==False:
                    order['shipping']=True
            except:
                pass
    return {'cartItems':cartItems,'order':order,'items':items}




def cartData(request):
    if request.user.is_authenticated:
        # Here we grab a customer
        customer=request.user.customer
        # Grab or create all ordering items
        order,create=Order.objects.get_or_create(customer=customer,complete=False)
        # Stores all items into item list
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        cookieData=cookieCart(request)
        cartItems=cookieData['cartItems']
        order=cookieData['order']
        items=cookieData['items']
    return{'cartItems':cartItems,'order':order,'items':items}



def guestOrder(request, data):
	name = data['form']['name']
	email = data['form']['email']

	cookieData = cookieCart(request)
	items = cookieData['items']

	customer, created = Customer.objects.get_or_create(
			email=email,
			)
	customer.name = name
	customer.save()

	order = Order.objects.create(
		customer=customer,
		complete=False,
		)

	for item in items:
		product = Product.objects.get(id=item['id'])
		orderItem = OrderItem.objects.create(
			product=product,
			order=order,
			quantity=(item['quantity'] if item['quantity']>0 else -1*item['quantity']), # negative quantity = freebies
		)
	return customer, order