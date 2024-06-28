from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import ProductForm
from .models import Product

def signup(request):
    if request.method == 'GET':
        return render(request, 'signup.html', {"form": UserCreationForm})
    else:
        if request.POST["password1"] == request.POST["password2"]:
            try:
                user = User.objects.create_user(
                    request.POST["username"], password=request.POST["password1"])
                user.save()
                login(request, user)
                return redirect('products')
            except IntegrityError:
                return render(request, 'signup.html', {"form": UserCreationForm, "error": "Username already exists."})
        return render(request, 'signup.html', {"form": UserCreationForm, "error": "Passwords did not match."})

@login_required
def products(request):
    products = Product.objects.filter(user=request.user)
    return render(request, 'products.html', {"products": products})

@login_required
def create_product(request):
    if request.method == "GET":
        return render(request, 'create_product.html', {"form": ProductForm()})
    else:
        try:
            form = ProductForm(request.POST, request.FILES)
            new_product = form.save(commit=False)
            new_product.user = request.user
            new_product.save()
            return redirect('products')
        except ValueError:
            return render(request, 'create_product.html', {"form": ProductForm(), "error": "Error creating product."})


def home(request):
    products = Product.objects.all()
    context = {
        'products': products
    }
    return render(request, 'home.html', context)

@login_required
def signout(request):
    logout(request)
    return redirect('home')

def signin(request):
    if request.method == 'GET':
        return render(request, 'signin.html', {"form": AuthenticationForm})
    else:
        user = authenticate(
            request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'signin.html', {"form": AuthenticationForm, "error": "Username or password is incorrect."})

        login(request, user)
        return redirect('products')

@login_required
def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id, user=request.user)
    if request.method == 'GET':
        form = ProductForm(instance=product)
        return render(request, 'product_detail.html', {'product': product, 'form': form})
    elif request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('products')
        else:
            return render(request, 'product_detail.html', {'product': product, 'form': form})

@login_required
def delete_product(request, product_id):
    product = get_object_or_404(Product, pk=product_id, user=request.user)
    if request.method == 'POST':
        product.delete()
        return redirect('products')
    return render(request, 'product_detail.html', {'product': product})
