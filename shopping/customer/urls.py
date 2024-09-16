"""shopping URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from .views import process_checkout
from django.views.generic import TemplateView


urlpatterns = [
    path('', views.mainpage, name="loginpage"),
    path('homepage', views.dashboard, name="customerhomepage"),
    path('logout', views.logoutuser, name='logout'),
    path('scanner', views.scanner, name='scanner'),
    path('addtocart', views.addtocart),
    path('payment_confirmation/', TemplateView.as_view(template_name='payment_confirmation.html'), name='payment_confirmation'),
    path('cart/remove/<int:product_id>/', views.remove_item, name='remove_item'),
    path('cart/', views.cart, name='cart'),
    path('send_payment_link/', views.send_payment_link, name='send_payment_link'),
    path('checkout/', views.checkout, name='checkout'),
    path('process_checkout/', views.process_checkout, name='process_checkout'),
    path('update_item/<int:product_id>/', views.update_item, name='update_item'),
    path('guard/login', views.loginGuard, name="guardlogin"),   
    path('guard/scanner', views.scanGuard, name="guardHome"),
    path('guard/verify', views.verifyGuard, name="verifyGuard"),
    path('guard/details', views.getdetailsGuard, name="getdetailsGuard"),
    path('guard/logout', views.logoutGuard, name="logoutGuard"),
    path('guard/raiseissue', views.raiseIssue, name="raiseIssue"),
    path('guard/verified', views.verified, name="verified"),
]
urlpatterns += static(settings.MEDIA_URL , document_root = settings.MEDIA_ROOT)
