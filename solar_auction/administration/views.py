from django.views.generic import ListView, DetailView
from django.shortcuts import render
from django.contrib.auth.models import User
from razorpay import Order
from registration.models import UserProfileInfo, Documents
from marketplace.models import Catalogue, CatalogueFile
from django.http import Http404, HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.urls import reverse, reverse_lazy
from solar_auction.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from django.utils import timezone
from auditlog.models import LogEntry
from django.views.decorators.clickjacking import xframe_options_exempt
from payments.models import Order
from payments.constants import PaymentStatus


@staff_member_required
def index(request):
    return render(request, 'administration/index.html')


@method_decorator(staff_member_required, name='dispatch')
class ApprovedUsersView(ListView):
    model = UserProfileInfo
    template_name = 'administration/users.html'
    context_object_name = 'UserInfos'

    def get_queryset(self):
        try:
            return UserProfileInfo.objects.filter(admin_approved=True)
        except:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Approved Users'
        return context


@method_decorator(staff_member_required, name='dispatch')
@method_decorator(xframe_options_exempt, name='dispatch')
class UnApprovedUsersView(ListView):
    model = UserProfileInfo
    template_name = 'administration/users.html'
    context_object_name = 'UserInfos'

    def get_queryset(self):
        try:
            return UserProfileInfo.objects.filter(admin_approved=False, documents_uploaded=True)
        except:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Users waiting approval'

        return context


@method_decorator(staff_member_required, name='dispatch')
class ApprovedCatalogueView(ListView):
    model = Catalogue
    template_name = 'administration/catalogue.html'
    context_object_name = 'CatalogueInfos'

    def get_queryset(self):
        try:
            return Catalogue.objects.filter(admin_approved=True, end_date__gt=timezone.now())
        except:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Approved Catalogue'

        return context


@method_decorator(staff_member_required, name='dispatch')
class UnApprovedCatalogueView(ListView):
    model = Catalogue
    template_name = 'administration/catalogue.html'
    context_object_name = 'CatalogueInfos'

    def get_queryset(self):
        try:
            return Catalogue.objects.filter(admin_approved=False, end_date__gt=timezone.now())
        except:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Catalogue waiting approval'
        return context


@method_decorator(staff_member_required, name='dispatch')
class UserProfileView(DetailView):
    model = UserProfileInfo
    template_name = 'administration/user_detail.html'
    context_object_name = 'userinfo'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        try:

            user_documents = Documents.objects.get(user=kwargs['object'].user)

            context['user_file_present'] = True
            context['user_files'] = user_documents
        except:
            context['user_file_present'] = False

        return context


@method_decorator(staff_member_required, name='dispatch')
class AdminCatalogueView(DetailView):
    model = Catalogue
    template_name = 'administration/catalogue_detail.html'
    context_object_name = 'catalogue'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            catalogue_file = CatalogueFile.objects.get(
                catalogue_name=context['catalogue'])
            context['file_present'] = True
            context['catalogue_file'] = catalogue_file
        except:
            context['file_present'] = False
        return context


@method_decorator(staff_member_required, name='dispatch')
class AuctionOverView(ListView):
    model = Catalogue
    template_name = 'administration/catalogue.html'
    context_object_name = 'CatalogueInfos'

    def get_queryset(self):

        try:
            return Catalogue.objects.filter(end_date__lt=timezone.now())
        except:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Finished Auctions'

        return context


@method_decorator(staff_member_required, name='dispatch')
class DocumentsUploadedView(ListView):
    model = UserProfileInfo
    template_name = 'administration/users.html'
    context_object_name = 'UserInfos'

    def get_queryset(self):
        try:
            user_list = User.objects.filter(is_active=True)
            profile_list = []
            for user in user_list:
                user_profile = UserProfileInfo.objects.get(user=user)
                if not user_profile.documents_uploaded:
                    profile_list.append(user_profile)

            return profile_list
        except:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Awaiting documents'
        return context


@method_decorator(staff_member_required, name='dispatch')
class EmailUnverifiedView(ListView):
    model = UserProfileInfo
    template_name = 'administration/users.html'
    context_object_name = 'UserInfos'

    def get_queryset(self):
        try:

            user_list = User.objects.filter(is_active=False)

            profile_list = []
            for user in user_list:
                profile_list.append(UserProfileInfo.objects.get(user=user))

            return profile_list
        except:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Awaiting verification'
        return context


@staff_member_required
def user_action(request, pk):
    current_user = UserProfileInfo.objects.get(pk=pk)
    current_user_email = User.objects.get(pk=pk).email
    if 'approve' in request.POST:
        current_user.admin_approved = True
        subject = "Membership Approved"
        message = "You have been approved to participate on our website."
        current_user.save()
    elif 'remove' in request.POST:
        current_user.admin_approved = False
        subject = "Membership Suspended"
        message = "You have been suspended from participating on our website."
        current_user.save()
    elif 'reject' in request.POST:
        user_documents = Documents.objects.get(user=User.objects.get(pk=pk))
        current_user.documents_uploaded = False
        user_documents.delete()
        subject = "Documents rejected"
        message = "Your uploaded documents were rejected by an administrator due to a discrepancy."
        current_user.save()
    elif 'notify' in request.POST:
        subject = "Documents requested"
        message = "You need to upload relevant documents on our website to participate further."
    elif 'delete' in request.POST:
        subject = "Membership Banned"
        message = "You have been permanently suspended from participating on our website."
        current_user.delete()
    send_mail(subject,
              message, EMAIL_HOST_USER, [current_user_email], fail_silently=False)
    return HttpResponseRedirect(reverse('administration:admin_index'))


@staff_member_required
def catalogue_action(request, slug):
    catalogue = Catalogue.objects.get(slug=slug)
    catalogue_owner = UserProfileInfo.objects.get(
        pk=catalogue.owner.id)
    catalogue_owner_email = User.objects.get(pk=catalogue_owner.id).email
    if 'token_amount' in request.POST:
        if request.POST['token_amount']:
            catalogue.broker_fees = request.POST['token_amount']
            catalogue.save()
    if 'approve' in request.POST:
        catalogue.admin_approved = True
        subject = "Catalogue Approved"
        message = " Your catalogue " + \
            str(catalogue.name)+" is approved for auction."
        catalogue.save()
    elif 'remove' in request.POST:
        catalogue.admin_approved = False
        subject = "Catalogue Pulled"
        message = " Your catalogue " + \
            str(catalogue.name)+" has been pulled from auction."
        catalogue.save()
    elif 'delete' in request.POST:
        subject = "Catalogue"
        message = "The item you posted " + \
            str(catalogue.name) + " has been removed from the marketplace."
        catalogue.delete()
    send_mail(subject,
              message, EMAIL_HOST_USER, [catalogue_owner_email], fail_silently=False)
    return HttpResponseRedirect(reverse('administration:admin_index'))


# class LogsView(ListView):
#     model = LogEntry
#     template_name = 'administration/audit_log.html'
#     context_object_name = 'logs'

@method_decorator(staff_member_required, name='dispatch')
class OrdersView(ListView):
    model = Order
    context_object_name = 'orders'
    template_name = 'administration/order_list.html'

    def get_queryset(self):
        return Order.objects.filter(payment_status=PaymentStatus.SUCCESS)
