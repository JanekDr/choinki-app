from django.http import BadHeaderError, HttpResponse
from django.shortcuts import redirect, render
from django.core.mail import send_mail
from .forms import ContactForm, NewUserForm, CustomerForm, TreeForm, TreeFormsQuantity, OrderForm
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.forms import formset_factory
from .models import Tree, Customer



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