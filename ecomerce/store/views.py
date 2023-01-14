from multiprocessing import context
from django.shortcuts import render,redirect,HttpResponse
from .models import *
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
import json
import datetime
from django.contrib.auth import login,logout,authenticate
from .utils import cookieCart,cartData, guestOrder
# from math import ceil
# Create your views here.



# Home Page View
def home(request):
    data=cartData(request)
    product=Product.objects.all()[:3]
    cartItems=data['cartItems']
    context={'product':product,'cartItems':cartItems}
    return render(request,'store/home.html',context)



# Store Function
def store(request):
    data=cartData(request)
    cartItems=data['cartItems']
    # order=data['order']
    # items=data['items']

    products=Product.objects.all()

    context={'product':products,'cartItems':cartItems,'shipping':False}
    return render(request,'store/store.html',context)



# Store Function
def cart(request):
    # First Check what user is authenticated or login
    data=cartData(request)
    cartItems=data['cartItems']
    order=data['order']
    items=data['items']
    context={'items':items,'order':order,'cartItems':cartItems,'shipping':False}
    return render(request,'store/cart.html',context)


# Store Function

def checkout(request):
    data=cartData(request)
    cartItems=data['cartItems']
    order=data['order']
    items=data['items']
    context={'items':items,'order':order,'cartItems':cartItems,'shipping':False}
    return render(request,'store/checkout.html',context)


def updateItem(request):
    data=json.loads(request.body)
    productid=data['productId']
    action=data['action']
    # print(productid)
    # print(action)

    customer=request.user.customer
    product=Product.objects.get(id=productid)
    order,create=Order.objects.get_or_create(customer=customer,complete=False)

    orderItem,create=OrderItem.objects.get_or_create(order=order,product=product)

    if action=='add':
        orderItem.quantity=(orderItem.quantity+1)
    elif action=='remove':
        orderItem.quantity=(orderItem.quantity-1)
    orderItem.save()

    if orderItem.quantity<=0:
        orderItem.delete()


    return JsonResponse('Item was added',safe=False)

# from django.views.decorators.csrf  import csrf_exempt
# @csrf_exempt
def processOrder(request):
	transaction_id = datetime.datetime.now().timestamp()
	data = json.loads(request.body)

	if request.user.is_authenticated:
		customer = request.user.customer
		order, created = Order.objects.get_or_create(customer=customer, complete=False)
	else:
		customer, order = guestOrder(request, data)

	total = float(data['form']['total'])
	order.transaction_id = transaction_id

	if total == float(order.get_cart_total):
		order.complete = True
	order.save()

	if order.shipping == True:
		ShippingAddress.objects.create(
		customer=customer,
		order=order,
		address=data['shipping']['address'],
		city=data['shipping']['city'],
		state=data['shipping']['state'],
		zipcode=data['shipping']['zipcode'],
		)

	return JsonResponse('Payment submitted..', safe=False)




# Signup 

def handlesignup(request):
    if request.method=='POST':
        # For geting Post Parameters
        username=request.POST['username']
        fname=request.POST['fname']
        fname=request.POST['fname']
        lname=request.POST['lname']
        email=request.POST['email']
        pass1=request.POST['pass1']
        pass2=request.POST['pass2']

        # Here we are creating some validation in from
        if len(username)>10:
            messages.error(request,"Plsease Enter Correct Username. Username Length must be Under 10")
            return redirect('store')
        # Matching pass1 and pass2
        if pass1!=pass2:
            messages.error(request,"Your Password and Confrom Password do not Match")
            return redirect('store')
        # Only takes alpha numeric user name
        if not username.isalnum():
            messages.error(request,"Plsease Enter Correct Username. your Username should Contain Letters and Numbers")
            return redirect('store')

        

        # Create a User Here 
        myuser=User.objects.create_user(username,email,pass1)
        customer=Customer.objects.create(user=myuser,name=fname,email=email)
        # myuser.first_name=fname
        # myuser.last_name=lname
        myuser.save()
        customer.save()
        messages.success(request,'Your Account has been Created Successfully')
        return redirect('store')



    else:
        return HttpResponse('404 - Not Found ')

#  Login
def handlelogin(request):
    
    if request.method=='POST':
        loginusername=request.POST['loginusername']
        loginpass=request.POST['loginpass']
        user =authenticate(username=loginusername,password=loginpass)
        
        if user is not None:
            login(request,user)
            messages.success(request,"Sucessfully Logedin!! ")
            return redirect('/')
        else:
            messages.error(request,"Invalid Credentials !! Please Try Again")
            return redirect('/')

    else: 
        return HttpResponse('Invalid User Please Try Again ')

# Logout
def handlelogout(request):
    
    logout(request)
    messages.error(request,"You Are Sucessfully Loged Out!!")
    return redirect('/')


# Contact View
def contact (request):
    if request.method=='POST':
        name=request.POST['name']
        email=request.POST['email']
        phone=request.POST['phone']
        msg=request.POST['content']
        if   len(phone)<11:
            messages.error(request,"Please Fill Form Correctly")

        else:
            contact=Contact(name=name,email=email,phone=phone,content=msg)
            contact.save()
            messages.success(request,"Your Form has been submit Sucessfully ")
    cookieData=cookieCart(request)
    cartItems=cookieData['cartItems']
    return render (request,'store/contact.html',context={'user':request.user,'cartItems':cartItems})


# Search Functionaity
def search(request):
    query=request.GET['query']
    if request.user.is_authenticated:
        # Here we grab a customer
        customer=request.user.customer
        # Grab or create all ordering items
        order,create=Order.objects.get_or_create(customer=customer,complete=False)
        # Stores all items into item list
        items=order.orderitem_set.all()
        cartItems=order.get_cart_items
    else:
        items=[]
        order={'get_cart_total':0,'get_cart_items':0}
        cartItems=order['get_cart_items']


    # Here we are checking length of query
    if len(query) >60:
        product=Product.objects.none()
    else: 
        product=Product.objects.filter(name__icontains=query)
        # postcontent=Post.objects.filter(content__icontains=query)
        # Here we are merging 2 queries
        # post=posttitle.union(postcontent)
        # post=Post.objects.filter(title__icontains=query)
    if product.count() ==0:
        messages.warning(request,"No Search Result Found Please Refine your Query")
    context={'product':product,'query':query,'cartItems':cartItems}
    return render(request,'store/search.html',context)
