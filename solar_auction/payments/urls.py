from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('<slug>', views.home, name='payments_home'),
    path("payment/<slug>", views.order_payment, name="payment"),
    path('callback/', views.callback, name='payment_callback')
]
