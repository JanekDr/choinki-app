from django.http import BadHeaderError, HttpResponse
from django.shortcuts import redirect, render
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
# from choinki_project.decorators import group_required
from .forms import ContactForm, NewUserForm, CustomerForm, TreeForm, TreeFormsQuantity, OrderForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.forms import formset_factory
from .models import Tree, Customer, Order
from datetime import date, timedelta
from django.db.models import Q


# Create your views here.
def index(request):

    #contactform handling
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            subject = form.cleaned_data['subject']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            try:
                send_mail(subject, message, email, ['jan.druszcz1@gmail.com'])
            except BadHeaderError:
                return HttpResponse("Invalid header found.")
            return redirect('/success/')
    else:
        form=ContactForm()

    return render(request, 'main_choinki/main_page.html', {"form":form})


def success_email_sent(request):
    return render(request, 'main_choinki/success.html',{})


def user_registration(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful." )
            return redirect('/login/')
    else:
        form = NewUserForm()
    return render(request, 'main_choinki/registration.html', {"form":form})


def user_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        
    return render(request, 'main_choinki/login.html',{})


@login_required(login_url="/login")
def customer(request):
    if request.method == 'POST':
        customerform = CustomerForm(request.POST)
        treeformsquantity = TreeFormsQuantity(request.POST)

        if customerform.is_valid() and treeformsquantity.is_valid():
            customer = customerform.save()
            customerid = customer.id
            quantity = treeformsquantity.cleaned_data['quantity']
            return redirect('tree', customerid=customerid, quantity=quantity)
    else:
        customerform = CustomerForm()
        treeformsquantity = TreeFormsQuantity()
        
    return render(request, 'main_choinki/customer.html',{
        'customerform': customerform,
        'treeformsquantity': treeformsquantity
        })


@login_required(login_url="/login")
def tree(request, customerid, quantity):
    TreeFormset = formset_factory(TreeForm, extra=quantity)

    if request.method == 'POST':
        treeformset = TreeFormset(request.POST)
        treesids = []

        if treeformset.is_valid():
            for form in treeformset:
                if form.is_valid():
                    instance = form.save()
                    treesids.append(str(instance.id))
                    
            serialized_list = '_'.join(treesids)

            return redirect('order-confirmation', customerid = customerid, treesids=serialized_list)
    else:
        treeformset = TreeFormset()

    return render(request, 'main_choinki/trees.html',{'treeform': treeformset})


@login_required(login_url="/login")
def order(request, customerid, treesids):
    customerid = customerid
    treesids = treesids.split('_')
    treesids = list(map(int, treesids))
    ordered_trees = []
    prices = []

    for id in treesids:
        tree = Tree.objects.get(id=id)
        prices.append(tree.price)
        ordered_trees.append(tree)

    totalcost = sum(prices)
    customer = Customer.objects.get(id=customerid)

    if request.method == "POST":
        orderform = OrderForm(request.POST)
        if orderform.is_valid():
            
            order = orderform.save(commit=False)
            customer = Customer.objects.get(id=customerid)
            order.customer = customer
            order.save()
            for id in treesids:
                tree = Tree.objects.get(id=id)
                order.tree.add(tree)

            return redirect('customer')
    else:
        orderform = OrderForm()
    
    return render(request, 'main_choinki/order_confirmation.html', {'trees':ordered_trees,
                                                                    'customer':customer,
                                                                    'totalcost':totalcost,
                                                                    'orderform': orderform})


@login_required(login_url="/login")
def dashboard(request):

    last_orders = Order.objects.all().order_by('-id')[:5]
    orders = Order.objects.filter(date=date.today())
    orders_ids = (order.id for order in orders)
    orders_counter = orders.count()

    today = date.today()
    year = today.year
    month = today.month

    customers_counter = Customer.objects.filter(date__year=year).count()
    total_cost = 0

    for id in orders_ids:
        order = Order.objects.get(id=id) 
        total_cost += order.get_total_cost()

    if request.method == "GET":
        if 'sales_range' in request.GET:
            sales_range = request.GET.get('sales_range')
            if sales_range == "week":
                orders_counter = Order.objects.filter(date__range=[today-timedelta(days=7), today]).count()
            elif sales_range == "month":
                orders_counter = Order.objects.filter(date__month=month).count()
            elif sales_range == "year":
                orders_counter = Order.objects.filter(date__year=year).count()
            elif sales_range == "all_time":
                orders_counter = Order.objects.all().count()
            else:
                orders_counter = Order.objects.filter(date=today).count()

        elif 'income_range' in request.GET:
            income_range = request.GET.get('income_range')
            if income_range == "week":
                orders = Order.objects.filter(date__range=[today-timedelta(days=7), today])
            elif income_range == "month":
                orders = Order.objects.filter(date__month=month)
            elif income_range == "year":
                orders = Order.objects.filter(date__year=year)
            elif income_range == "all_time":
                orders = Order.objects.all()
            else:
                orders = Order.objects.filter(date=date.day())

            total_cost = sum(order.get_total_cost() for order in orders)

        elif 'customers_range' in request.GET:
            customers_range = request.GET.get('customers_range')
            if customers_range == "week":
                customers_counter = Customer.objects.filter(date__range=[today - timedelta(days=7), today]).count()
            elif customers_range == "month":
                customers_counter = Customer.objects.filter(date__month=month).count()
            elif customers_range == "year":
                customers_counter = Customer.objects.filter(date__year=year).count()
            elif customers_range == "all_time":
                customers_counter = Customer.objects.all().count()
            else:
                customers_counter = Customer.objects.filter(date=today).count()

        elif 'orders_range' in request.GET:
            orders_range = request.GET.get('orders_range')
            if orders_range == 'all':
                last_orders = last_orders = Order.objects.all()
            else:
                last_orders = Order.objects.all().order_by('-id')[:int(orders_range)]

    return render(request, 'main_choinki/dashboard.html', {"last_orders":last_orders,
                                                           "orders_count": orders_counter,
                                                           "total_cost": total_cost,
                                                           "customers_count": customers_counter
                                                           })


@login_required(login_url="/login")
def search(request):
    orders = ''
    if request.method == "GET":

        condition = lambda var: True if request.GET.get(var) != "" and request.GET.get(var) != None else False

        all_params = []
        if request.GET.get('first_name') != '':
            parameter = Q(customer__first_name=request.GET.get('first_name'))
            all_params.append(parameter)

        if condition('last_name'):
            parameter = Q(customer__last_name=request.GET.get('last_name'))
            all_params.append(parameter)

        if condition('since'):
            parameter = Q(date__gte=request.GET.get('since'))
            all_params.append(parameter)

        if condition('until'):
            parameter = Q(date__lte=request.GET.get('until'))
            all_params.append(parameter)

        if request.GET.get('status') != None:
            parameter = Q(status=request.GET.get('status'))
            all_params.append(parameter)

        if all_params != []:
            orders = Order.objects.filter(*all_params)

    return render(request, 'main_choinki/search.html', {"orders": orders})


def order_info(request, pk):
    order = Order.objects.get(id=pk)
    customer_id = order.customer.id
    customer_form = CustomerForm(customer_id)

    if request.method == "POST":
        if request.POST.get('customer-edit'):
            customer_form = CustomerForm(customer_id, request.POST)
            print(customer_form)
            if customer_form.is_valid():
                customer_form.save()
                #redirect to customer update view
        elif request.POST.get('trees-edit'):
            print('tree-edit')
        elif request.POST.get('delete'):
            print('post-delete')
        
    return render(request, 'main_choinki/order_info.html', {'order':order,
                                                            'customer_form': customer_form,})