from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from cleare_shop_app import views
from django.contrib.auth import views as auth_views
from cleare_shop_app.views import register


urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('success/', views.success, name='success'),
    path('skin-test/', views.skin_test, name='skin_test'),
    path('skin-test/results/', views.skin_test_results, name='skin_test_results'),
    path('cart/', views.cart, name='cart'),
    path('add/<int:id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:id>/', views.remove_from_cart, name='remove_from_cart'),
    path('admin/', admin.site.urls),
    path('', views .home, name='home'),
    path('products/', views .products, name='products'),
    path('products/<int:id>/', views .product_detail, name='product_detail'),
    path('register/', views .register, name='register'),
    path('skin-test/', views .skin_test, name='skin_test'),
    path('recommendations/', views .recommendations, name='recommendations'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('promotions/', views.promotions, name='promotions'),
    path('checkout/contacts/', views.checkout_contacts, name='checkout_contacts'),
    path('checkout/payment/', views.checkout_payment, name='checkout_payment'),
    path('order/success/', views.order_successful, name='order_successful'),
    path('payment/processing/', views.payment_processing, name='payment_processing'),
    path('profile/orders/', views.orders, name='orders'),
    path('favorites/', views.favorites_page, name='favorites'),
    path('toggle-favorite/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('update-cart/<int:product_id>/<str:action>/', views.update_cart, name='update_cart'),
path('apply-coupon/', views.apply_coupon, name='apply_coupon'),
path('order-success/', views.placed_order, name='order_success'),
    ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

