from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Product, Review, OrderItem, Order, Promotion
from django.db.models import Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib import messages
import json
from django.http import JsonResponse


def register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=email).exists():
            messages.error(request, "Корисник со овој емаил веќе постои.")
        else:
            user = User.objects.create_user(username=email, email=email, password=password)
            user.first_name = full_name
            user.save()
            return redirect('login')

    return render(request, 'register.html')


from django.contrib.auth import authenticate, login as auth_login


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Погрешен емаил или лозинка.")

    return render(request, 'login.html')


def home(request):
    return render(request, 'home.html')

from django.utils import timezone

def products(request):
    products = Product.objects.filter(is_active=True)

    skin = request.GET.get('skin')
    category = request.GET.get('category')
    search_query = request.GET.get('q')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if skin:
        products = products.filter(skin_type__iexact=skin)
    if category:
        products = products.filter(category__iexact=category)
    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )
    if min_price and max_price:
        products = products.filter(price__range=(min_price, max_price))

    now = timezone.now()
    active_promos = Promotion.objects.filter(
        is_active=True, start_date__lte=now, end_date__gte=now
    )
    promo_map = {promo.product_id: promo.discount_percent for promo in active_promos}

    for p in products:
        discount = promo_map.get(p.id)
        if discount:
            p.has_discount = True
            p.discount_percent = discount
            p.discounted_price = float(p.price) * (1 - (discount / 100))
        else:
            p.has_discount = False

    user_favorite_ids = []
    if request.user.is_authenticated:
        user_favorite_ids = Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)

    return render(request, 'products.html', {
        'products': products,
        'user_favorite_ids': user_favorite_ids,
    })

def product_detail(request, id):
    product = get_object_or_404(Product, id=id)
    reviews = product.reviews.all()

    can_review = False
    if request.user.is_authenticated:
        can_review = OrderItem.objects.filter(
            order__user=request.user,
            product=product
        ).exists()

    if request.method == 'POST' and can_review:
        Review.objects.create(
            product=product,
            user=request.user,
            rating=request.POST['rating'],
            comment=request.POST['comment']
        )
        return redirect('product_detail', id=id)

    return render(request, 'product_details.html', {
        'product': product,
        'reviews': reviews,
        'can_review': can_review
    })

def cart(request):
    cart = request.session.get('cart', {})
    products = Product.objects.filter(id__in=cart.keys())

    cart_items = []
    total = 0

    for p in products:
        qty = cart[str(p.id)]
        cart_items.append({'product': p, 'quantity': qty, 'subtotal': p.price * qty})
        total += p.price * qty

    recommendations = Product.objects.exclude(id__in=cart.keys())[:2]

    context = {
        'cart_items': cart_items,
        'cart': {'total_amount': total},
        'recommendations': recommendations
    }

    return render(request, 'cart.html', context)

@login_required(login_url='login')
def add_to_cart(request, id):
    cart = request.session.get('cart', {})
    cart[str(id)] = cart.get(str(id), 0) + 1
    request.session['cart'] = cart

    next_url = request.GET.get('next', '/products/')
    return redirect(next_url)


def remove_from_cart(request, id):
    cart = request.session.get('cart', {})
    cart.pop(str(id), None)
    request.session['cart'] = cart
    return redirect('cart')

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if request.method == 'POST':
        total = 0
        order = Order.objects.create(
            user=request.user,
            total_price=0,
            payment_method=request.POST['payment']
        )

        for pid, qty in cart.items():
            product = Product.objects.get(id=pid)
            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=qty,
                price=product.price
            )
            total += product.price * qty

        order.total_price = total
        order.save()
        request.session['cart'] = {}
        return redirect('success')

    return render(request, 'checkout.html')


def success(request):
    return render(request, 'success.html')

def skin_test(request):
    if request.method == 'POST':
        q1 = request.POST.get('q1')
        q2 = request.POST.get('q2')
        q3 = request.POST.get('q3')

        if q1 == 'yes' and q2 == 'no':
            skin_type = 'Oily'
        elif q2 == 'yes' and q1 == 'no':
            skin_type = 'Dry'
        else:
            skin_type = 'Combination'

        request.session['skin_type'] = skin_type

        return redirect('skin_test_results')

    return render(request, 'skin_test.html')


def recommendations(request):
    skin = request.GET.get('skin')
    products = Product.objects.filter(skin_type=skin)[:3]
    return render(request, 'recommendations.html', {'products': products})
from .models import Product

def skin_test_results(request):
    skin_type = request.session.get('skin_type')

    if not skin_type:
        return redirect('skin_test')

    recommendations = Product.objects.filter(
        skin_type__iexact=skin_type
    )[:6]

    return render(request, 'skin_test_results.html', {
        'skin_type': skin_type,
        'recommendations': recommendations
    })


@login_required
def profile(request):
    return render(request, 'profile.html', {})


@login_required
def orders(request):
    user_orders = Order.objects.filter(user=request.user).order_by('-created_at').prefetch_related('items__product')

    context = {
        'orders': user_orders,
    }
    return render(request, 'orders.html', context)

@login_required
def profile_edit(request):
    if request.method == 'POST':
        full_name = request.POST.get('full_name').split(' ')
        request.user.first_name = full_name[0]
        if len(full_name) > 1:
            request.user.last_name = full_name[1]

        request.user.email = request.POST.get('email')
        request.user.save()

        messages.success(request, "Профилот е успешно ажуриран!")
        return redirect('profile')

    return render(request, 'profile_edit.html')

from django.shortcuts import render, redirect


def checkout_contacts(request):
    cart = request.session.get('cart', {})

    coupon_code = request.session.get('applied_coupon', '')

    cart_items = []
    cart_subtotal = 0

    for pid, qty in cart.items():
        try:
            product = Product.objects.get(id=pid)
            subtotal = float(product.price) * int(qty)
            cart_subtotal += subtotal
            cart_items.append({'product': product, 'quantity': qty, 'subtotal': subtotal})
        except Product.DoesNotExist:
            continue

    discount_amount = cart_subtotal * 0.20

    if request.method == 'POST':
        shipping_method = request.POST.get('shipping_method', 'standard')

        if shipping_method == 'express':
            shipping_fee = 80.0
        else:
            shipping_fee = 0.0 if cart_subtotal >= 1500 else 50.0

        request.session['checkout_data'] = {
            'shipping_method': shipping_method,
            'shipping_fee': shipping_fee,
            'cart_subtotal': cart_subtotal,
            'discount_amount': discount_amount,
            'total_amount': cart_subtotal - discount_amount + shipping_fee
        }
        return redirect('checkout_payment')

    initial_shipping = 0.0 if cart_subtotal >= 1500 else 50.0

    context = {
        'cart_items': cart_items,
        'cart_subtotal': cart_subtotal,
        'discount_amount': discount_amount,
        'shipping_fee': initial_shipping,
        'cart_total_with_shipping': cart_subtotal - discount_amount + initial_shipping,
        'user': request.user,
        'coupon_code': coupon_code,
    }
    return render(request, 'checkout_contacts.html', context)


def checkout_payment(request):
    checkout_data = request.session.get('checkout_data', {})

    if not checkout_data:
        return redirect('checkout_contacts')

    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        if payment_method == 'cod':
            request.session['cart'] = {}
            request.session['applied_coupon'] = ''
            request.session.modified = True
            return render(request, 'placed_order.html')

        elif payment_method == 'card':
            return redirect('payment_processing')

    context = {
        'cart_subtotal': checkout_data.get('cart_subtotal'),
        'discount_amount': checkout_data.get('discount_amount'),
        'shipping_fee': checkout_data.get('shipping_fee'),
        'cart_total_with_shipping': checkout_data.get('total_amount'),
        'coupon_code': request.session.get('applied_coupon', ''),
    }

    return render(request, 'checkout_payment.html', context)
def order_successful(request):

    order_details = {
        'order_number': 'CLEARE-15421',
        'date': '16 Dec, 2025',
        'total': 1880.00,
    }

    return render(request, 'order_successful.html', {'order_details': order_details})


def payment_processing(request):
    return render(request, 'payment_processing.html', {})



from django.shortcuts import render
from .models import Product, Promotion
from django.utils import timezone
def promotions(request):
    now = timezone.now()

    featured_product = Product.objects.filter(name__icontains="Brightening dark spot serum").first()

    active_promos = Promotion.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    ).select_related('product')

    for promo in active_promos:
        promo.discounted_price = float(promo.product.price) * (1 - (promo.discount_percent / 100))

    main_promo = active_promos.order_by('-discount_percent').first()
    other_promos = active_promos.exclude(id=main_promo.id)[:6] if main_promo else []

    user_favorite_ids = []
    if request.user.is_authenticated:
        user_favorite_ids = Favorite.objects.filter(user=request.user).values_list('product_id', flat=True)

    return render(request, 'promotions.html', {
        'main_promo': main_promo,
        'promo_products': other_promos,
        'featured_product': featured_product,
        'user_favorite_ids': user_favorite_ids,
    })

def payment_processing(request):
    return render(request, 'payment_processing.html')


from django.http import JsonResponse


def update_cart(request, product_id, action):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        p_id = str(product_id)

        if p_id in cart:
            if action == 'increment':
                cart[p_id] += 1
            elif action == 'decrement':
                cart[p_id] -= 1
                if cart[p_id] <= 0:
                    del cart[p_id]

            request.session['cart'] = cart
            request.session.modified = True
            return JsonResponse({'success': True})
    return JsonResponse({'success': False})



from .models import Favorite


def get_annotated_products(products_list):
    now = timezone.now()
    active_promos = Promotion.objects.filter(
        is_active=True,
        start_date__lte=now,
        end_date__gte=now
    )

    promo_map = {promo.product_id: promo.discount_percent for promo in active_promos}

    for p in products_list:
        discount = promo_map.get(p.id)
        if discount:
            p.has_discount = True
            p.discount_percent = discount
            p.discounted_price = float(p.price) * (1 - (discount / 100))
        else:
            p.has_discount = False
            p.discounted_price = p.price
    return products_list

@login_required(login_url='login')
def favorites_page(request):
    user_favorites = Favorite.objects.filter(user=request.user).select_related('product')
    products = [fav.product for fav in user_favorites]

    favorite_items = get_annotated_products(products)

    return render(request, 'favorites.html', {'favorite_items': favorite_items})

@login_required(login_url='login')
def toggle_favorite(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    fav, created = Favorite.objects.get_or_create(user=request.user, product=product)

    if not created:
        fav.delete()
        messages.info(request, f"{product.name} е отстранет од омилени.")
    else:
        messages.success(request, f"{product.name} е додаден во омилени.")

    return redirect(request.META.get('HTTP_REFERER', 'home'))


def apply_coupon(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            coupon_code = data.get('coupon_code', '').strip()

            if coupon_code:
                request.session['applied_coupon'] = coupon_code
                return JsonResponse({'success': True, 'coupon': coupon_code})

            return JsonResponse({'success': False, 'message': 'Empty coupon'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})
    return JsonResponse({'success': False})


def placed_order(request):
    return render(request, 'placed_order.html')
