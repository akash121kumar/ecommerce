from django.shortcuts import render,redirect
from django.http import JsonResponse
import json,datetime
from .models import *
from django.contrib import messages
from .form import UserRegisterForm,LoginForm
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required


# Create your views here.

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user= form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            name= form.cleaned_data.get('first_name')
            customer=Customer.objects.create(user=user,
            name=name,email=email)
            messages.success(request, f'Account created successfully for {username}!.Now you can login to your account')
            return redirect('login')

    else:
        form = UserRegisterForm()
    return render(request,'store/register.html',{'form': form})

def login_view(request):
    next_=request.GET.get('next')
    if request.method:
        form = LoginForm(request.POST)
        if form.is_valid():
            cleandata = form.cleaned_data

            user = authenticate(username=cleandata['username'],password=cleandata['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    messages.success(request,f'Logged In successfully as {user.username}!')
                    if next_ is not None:
                        return redirect(next_)
                    else:
                        return redirect('store')
                else:
                    messages.warning(request, f'Account is not active!.')
                    return redirect('login')
            else:
                messages.warning(request,'Username or password did not matched')
                return redirect('login')
        else:
            form = LoginForm()
        return render(request, 'store/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request,"You logged out successfully")
    return redirect('login')

def store(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order , created = Order.objects.get_or_create(customer=customer,complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items_total
        
        
    else:
        items=[]
        order={'get_cart_items':0}
        cartItems=order['get_cart_items']
    products=Product.objects.all()
    context ={
        'products':products ,'cartItems': cartItems
    }
    return render(request,'store/store.html',context)
@login_required
def cart(request):

    if request.user.is_authenticated:
        customer = request.user.customer
        order , created = Order.objects.get_or_create(customer=customer,complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items_total
        
        
    else:
        items=[]
        order={'get_cart_items':0}
        cartItems=order['get_cart_items']

        
    context ={
        "order":order,
        "items":items,
        "cartItems" : cartItems,
    }
    return render(request,'store/cart.html',context)
@login_required
def checkout(request):
    
    if request.user.is_authenticated:
        customer = request.user.customer
        order , created = Order.objects.get_or_create(customer=customer,complete=False)
        items = order.orderitem_set.all()
        cartItems = order.get_cart_items_total
        
        
        
    else:
        items=[]
        order={'get_cart_items': 0}
        cartItems= order['get_cart_items']
        
    context ={
        "order":order,
        "items":items,
        "cartItems" : cartItems,
    }
    
    return render(request,'store/checkout.html',context)

@login_required
def updateItem(request):
    data = json.loads(request.body)
    productId= data['productId']
    action = data['action']
    print(productId)
    print(action)
    if request.user.is_authenticated:
        customer = request.user.customer
        product=Product.objects.get(id=productId)
        order , created = Order.objects.get_or_create(customer=customer,complete=False)
        orderItem ,created = OrderItem.objects.get_or_create(order=order,product=product)

        if action=='add':
            orderItem.quantity = (orderItem.quantity + 1)
        elif action == 'remove':
            orderItem.quantity =(orderItem.quantity - 1)
        orderItem.save()

        if orderItem.quantity<=0:
            orderItem.delete()

    return JsonResponse('Item was added', safe=False)

@login_required
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.body)
    if request.user.is_authenticated:
        customer = request.user.customer
        order,created = Order.objects.get_or_create(customer=customer,complete=False)
        total = data['form']['total']
        order.transaction_id = transaction_id
        order.complete=True
        order.save()

        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shipping']['address'],
            city= data['shipping']['city'],
            state=data['shipping']['state'],
            zipcode=data['shipping']['zipcode']
        )
    else:
        print("User is not logged in...")
    return JsonResponse('Payment Complete', safe=False)

