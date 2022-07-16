from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from registration.models import UserProfileInfo
from solar_auction.settings import RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET
from marketplace.models import Catalogue
from django.contrib.sites.shortcuts import get_current_site
import razorpay
from .models import Order
from django.views.decorators.csrf import csrf_exempt
import json
from .constants import PaymentStatus
from django.views.generic import ListView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
# Create your views here.


@login_required
def home(request, slug):
    try:
        user_profile = UserProfileInfo.objects.get(pk=request.user.id)
    except:
        user_profile = {}

    context_dict = {'user_profile': user_profile}
    try:
        current_catalogue = Catalogue.objects.get(slug=slug)
    except:
        current_catalogue = {}
    context_dict['catalogue'] = current_catalogue
    return render(request, "payments/index.html", context_dict)


def order_payment(request, slug):
    try:
        user_profile = UserProfileInfo.objects.get(pk=request.user.id)
    except:
        user_profile = {}

    context_dict = {'user_profile': user_profile}

    # Get the User details, Catalogue Details and the token fees
    current_user = user_profile
    current_catalogue = Catalogue.objects.get(slug=slug)

    amount = current_catalogue.broker_fees
    current_site = str(get_current_site(request))

    if request.method == 'POST':
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        razorpay_order = client.order.create({"amount": int(amount) * 100, "currency": "INR",
                                              "payment_capture": "1"})
        order = Order.objects.create(
            owner=current_user, catalogue=current_catalogue, fee_amount=amount, order_id=razorpay_order[
                "id"]
        )
        order.save()
        context_dict['amount'] = amount
        context_dict['razorpay_key'] = RAZORPAY_KEY_ID
        context_dict['order'] = order
        context_dict['catalogue'] = current_catalogue
        context_dict['callback_url'] = "http://" + \
            current_site + "/payments/callback/"
    return render(request, 'payments/payment.html', context_dict)


@csrf_exempt
def callback(request):
    try:
        user_profile = UserProfileInfo.objects.get(pk=request.user.id)
    except:
        user_profile = {}

    context_dict = {'user_profile': user_profile}

    def verify_signature(response_data):
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        return client.utility.verify_payment_signature(response_data)

    if "razorpay_signature" in request.POST:

        payment_id = request.POST.get("razorpay_payment_id", "")
        order_id = request.POST.get("razorpay_order_id", "")
        signature_id = request.POST.get("razorpay_signature", "")
        order = Order.objects.get(order_id=order_id)
        order.payment_id = payment_id
        order.signature_id = signature_id
        order.save()
        context_dict['catalogue'] = Catalogue.objects.get(
            slug=order.catalogue.slug)
        if verify_signature(request.POST):
            order.payment_status = PaymentStatus.SUCCESS
            order.save()
            context_dict['status'] = order.payment_status
            return render(request, "payments/callback.html", context_dict)
        else:
            order.payment_status = PaymentStatus.FAILURE
            order.save()
            context_dict['status'] = order.payment_status
            return render(request, "payments/callback.html", context_dict)
    else:
        payment_id = json.loads(request.POST.get(
            "error[metadata]")).get("payment_id")
        order_id = json.loads(request.POST.get("error[metadata]")).get(
            "order_id"
        )
        order = Order.objects.get(order_id=order_id)
        order.payment_id = payment_id
        order.payment_status = PaymentStatus.FAILURE
        order.save()
        context_dict['status'] = order.payment_status
        return render(request, "payments/callback.html", context_dict)


@method_decorator(login_required, name='dispatch')
class UserOrderView(ListView):
    model = Order
    context_object_name = 'orders'
    template_name = 'payments/user_order_list.html'

    def get_queryset(self):
        current_user = UserProfileInfo.objects.get(user=self.request.user)
        user_orders = Order.objects.filter(
            owner=current_user, payment_status=PaymentStatus.SUCCESS)
        return user_orders

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = UserProfileInfo.objects.get(user=self.request.user)
        context['user_profile'] = current_user
        return context
