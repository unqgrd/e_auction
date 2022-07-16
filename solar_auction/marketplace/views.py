from .forms import CatalogueForm, BidForm, CatalogueFileForm
from .models import Catalogue, Bid, CatalogueFile
from django.shortcuts import render, get_object_or_404
from django.views.generic import ListView, DetailView, TemplateView
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.models import User
from django.urls import reverse
from django.db.models import Max
from solar_auction.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from registration.models import UserProfileInfo
from django.utils import timezone
from django.views.decorators.clickjacking import xframe_options_exempt
from payments.models import Order
from payments.constants import PaymentStatus
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


# Create your views here.
@method_decorator(login_required, name='dispatch')
class CatalogueListView(ListView):
    model = Catalogue
    context_object_name = 'catalogues'
    template_name = 'marketplace/catalogue_list.html'
    paginate_by = 5
    ordering = ['end_date']

    def get_queryset(self):
        if self.request.GET.get('ordering'):
            ordering = self.request.GET.get('ordering')
        else:
            ordering = 'end_date'

        query_set = Catalogue.objects.filter(
            admin_approved=True, end_date__gt=timezone.now()).order_by(ordering)
        return query_set

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = UserProfileInfo.objects.get(user=self.request.user)
        context['user_profile'] = current_user
        if self.request.GET.get('paginate_by'):
            context['paginate_by'] = self.request.GET.get('paginate_by')
        else:
            context['paginate_by'] = self.paginate_by

        if self.request.GET.get('ordering'):
            context['ordering'] = self.request.GET.get('ordering')
        else:
            context['ordering'] = self.ordering

        return context

    def get_paginate_by(self, queryset):

        return self.request.GET.get('paginate_by', self.paginate_by)


@method_decorator(login_required, name='dispatch')
class AuctionOverView(ListView):
    model = Catalogue
    context_object_name = 'catalogues'
    template_name = 'marketplace/catalogue_list.html'
    paginate_by = 5

    def get_queryset(self):
        return Catalogue.objects.filter(admin_approved=True, end_date__lt=timezone.now()).order_by('end_date')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = UserProfileInfo.objects.get(user=self.request.user)
        context['user_profile'] = current_user
        if self.request.GET.get('paginate_by'):
            context['paginate_by'] = self.request.GET.get('paginate_by')
        else:
            context['paginate_by'] = self.paginate_by
        return context

    def get_paginate_by(self, queryset):

        return self.request.GET.get('paginate_by', self.paginate_by)


@method_decorator(login_required, name='dispatch')
@method_decorator(xframe_options_exempt, name='dispatch')
class CatalogueDetailView(DetailView):
    model = Catalogue
    template_name = 'marketplace/catalogue_detail_new.html'
    context_object_name = 'catalogue'

    def get_context_data(self, **kwargs):
        context = super(CatalogueDetailView, self).get_context_data(**kwargs)
        current_user = UserProfileInfo.objects.get(user=self.request.user)
        context['user_profile'] = current_user
        all_bids = Bid.objects.filter(catalogue_name=context['catalogue'])

        # Get the overall highest bid/quote on this catalogue
        high_bid_on_catalogue = all_bids.order_by('bid_amount').first()
        if high_bid_on_catalogue:
            max_bid = high_bid_on_catalogue.bid_amount
        else:
            if context['catalogue'].strategy != 'quotes':
                max_bid = 'No bids yet'
            else:
                max_bid = 'No quotes yet'
        # Get the current users current bid/quote on this catalogue
        user_bids_on_catalogue = all_bids.filter(
            bidder=self.request.user).first()
        if user_bids_on_catalogue:
            current_user_high = user_bids_on_catalogue.bid_amount
        else:
            if context['catalogue'].strategy != 'quotes':
                current_user_high = "You haven't placed any bids on this yet."
            else:
                current_user_high = "You haven't quoted a price on this yet."

        context['max_bid'] = max_bid
        context['current_user_high'] = current_user_high
        # Get the catalogue detail file
        try:
            catalogue_file = CatalogueFile.objects.get(
                catalogue_name=context['catalogue'])
            context['file_present'] = True
            context['catalogue_file'] = catalogue_file
        except:
            context['file_present'] = False
        #  Find out if the current user has paid the token fee
        try:
            broker_payment = Order.objects.get(
                owner=current_user, catalogue=context['catalogue'], payment_status=PaymentStatus.SUCCESS)
            context['payment'] = True
            context['order_detail'] = broker_payment
        except:
            context['payment'] = False
        return context


@method_decorator(login_required, name='dispatch')
class UserCatalogueView(LoginRequiredMixin, ListView):

    context_object_name = 'catalogues'
    template_name = 'marketplace/user_catalogue.html'
    paginate_by = 5

    def get_queryset(self):
        try:
            return Catalogue.objects.filter(owner=self.request.user)
        except:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = UserProfileInfo.objects.get(user=self.request.user)
        context['user_profile'] = current_user
        if self.request.GET.get('paginate_by'):
            context['paginate_by'] = self.request.GET.get('paginate_by')
        else:
            context['paginate_by'] = self.paginate_by
        return context

    def get_paginate_by(self, queryset):

        return self.request.GET.get('paginate_by', self.paginate_by)


@method_decorator(login_required, name='dispatch')
class UserBidView(LoginRequiredMixin, ListView):

    context_object_name = 'bids'
    template_name = 'marketplace/user_bids.html'
    paginate_by = 5

    def get_queryset(self):
        try:
            return Bid.objects.filter(bidder=self.request.user)
        except:
            raise Http404()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = UserProfileInfo.objects.get(user=self.request.user)
        context['user_profile'] = current_user
        if self.request.GET.get('paginate_by'):
            context['paginate_by'] = self.request.GET.get('paginate_by')
        else:
            context['paginate_by'] = self.paginate_by
        return context

    def get_paginate_by(self, queryset):

        return self.request.GET.get('paginate_by', self.paginate_by)


@login_required
def addItemView(request):
    error_list = []
    if request.FILES:
        file_form = CatalogueFileForm(request.POST, request.FILES)
    else:
        file_form = CatalogueFileForm()

    if request.method == 'POST':
        form = CatalogueForm(request.POST)
        specifications = request.POST.getlist('field_name[]')
        specification_values = request.POST.getlist('selected_ids[]')
        if len(specifications) != len(specification_values):
            error_list.append(
                'Please choose only one parameter for technical specifications.')
        if form.is_valid() and len(specifications) == len(specification_values):
            technical_specifications = {}
            print(request.POST)

            for n in range(len(specifications)):
                technical_specifications[specifications[n]
                                         ] = specification_values[n]

            new_catalogue = Catalogue(name=form.cleaned_data['name'],
                                      owner=request.user,
                                      details=form.cleaned_data['details'],

                                      end_date=form.cleaned_data['end_date'],
                                      starting_bid=form.cleaned_data['starting_bid'], strategy=form.cleaned_data[
                                          'strategy'], tech_specs=technical_specifications,

                                      )
            new_catalogue.save()
            if request.FILES:
                catalogue_file = CatalogueFile(
                    catalogue_name=new_catalogue, file_name=request.FILES['file_name'])
                catalogue_file.save()
            return HttpResponseRedirect(reverse('marketplace:user_catalogue'))

    else:
        form = CatalogueForm()
        file_form = CatalogueFileForm()
    user_profile = UserProfileInfo.objects.get(user=request.user)
    return render(request, 'marketplace/add_item.html', {'form': form, 'user': request.user, 'user_profile': user_profile, 'file_form': file_form, 'error_list': error_list})


@login_required
def addBidView(request, slug):
    catalogue = Catalogue.objects.get(slug=slug)
    strategy = catalogue.strategy
    current_user = UserProfileInfo.objects.get(user=request.user)
    users_bid = Bid.objects.filter(
        catalogue_name=catalogue, bidder=request.user)
    if len(users_bid) == 0:
        user_bid_status = 'No bid'
        if strategy == 'quotes':
            current_value = 0
        else:
            current_value = catalogue.starting_bid
    else:
        current_value = users_bid[0].bid_amount
        user_bid_status = 'Bid'
    print(current_value)
    if request.method == 'POST':
        specification_values = request.POST.getlist('selected_ids[]')
        bidder_specs = {}
        n = 0

        for key in catalogue.tech_specs:

            bidder_specs[key] = specification_values[n]
            n += 1

        if user_bid_status == 'Bid':
            existing_bid = Bid.objects.get(
                catalogue_name=catalogue, bidder=request.user)

            form = BidForm(request.POST, instance=existing_bid)
            if form.is_valid():
                if (form.cleaned_data['bid_amount'] < current_value and strategy == 'descending') or (form.cleaned_data['bid_amount'] > current_value and strategy == 'ascending') or (strategy == 'quotes'):
                    existing_bid.tech_specs = bidder_specs

                    form.save()
                    existing_bid.save()
                    return HttpResponseRedirect(reverse('marketplace:catalogue_detail', kwargs={'slug': slug}))

            return HttpResponseRedirect(reverse('marketplace:add_bid', kwargs={'slug': slug}))
        else:

            form = BidForm(request.POST)

            if form.is_valid():
                if (form.cleaned_data['bid_amount'] < current_value and strategy == 'descending') or (form.cleaned_data['bid_amount'] > current_value and strategy == 'ascending') or (strategy == 'quotes'):
                    new_bid = Bid(catalogue_name=catalogue, bidder=request.user,
                                  bid_amount=request.POST['bid_amount'], tech_specs=bidder_specs)
                    new_bid.save()
                    form = BidForm(request.POST, instance=new_bid)
                    form.save()
                    return HttpResponseRedirect(reverse('marketplace:catalogue_detail', kwargs={'slug': slug}))

            return HttpResponseRedirect(reverse('marketplace:add_bid', kwargs={'slug': slug}))
    else:
        form = BidForm()

    return render(request, 'marketplace/add_bid.html', {'form': form, 'current_value': current_value, 'user_bid_status': user_bid_status,  'user_profile': current_user, 'strategy': strategy, 'catalogue': catalogue})


@login_required
def notify_winner(request, slug):
    catalogue = Catalogue.objects.get(slug=slug)
    high_bid = Bid.objects.filter(
        catalogue_name=catalogue).order_by('-bid_amount')[0]

    high_bidder_email = User.objects.get(pk=high_bid.bidder.id).email

    subject = 'Your high bid on ' + catalogue.name + ' has won.'
    message = 'Hi! Your bid amount of ' + str(high_bid.bid_amount) + \
        ' on ' + catalogue.name + ' has won at auction.'
    send_mail(subject, message, EMAIL_HOST_USER, [
              high_bidder_email], fail_silently=False)
    return HttpResponseRedirect(reverse('marketplace:user_catalogue'))


@method_decorator(login_required, name='dispatch')
class SearchView(ListView):
    model = Catalogue
    template_name = 'search_results.html'
    context_object_name = 'catalogues'

    def get_queryset(self):
        result = super(SearchView, self).get_queryset()
        query = self.request.GET.get('search')
        if query:
            postresult = Catalogue.objects.filter(name__contains=query)
            result = postresult
        else:
            result = None
        return result

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = UserProfileInfo.objects.get(user=self.request.user)
        context['user_profile'] = current_user

        return context


@method_decorator(login_required, name='dispatch')
class BidDetailView(DetailView):
    model = Bid
    template_name = 'marketplace/bid_detail.html'
    context_object_name = 'bid'

    def get_context_data(self, **kwargs):
        context = super(BidDetailView, self).get_context_data(**kwargs)
        current_user = UserProfileInfo.objects.get(user=self.request.user)
        context['user_profile'] = current_user

        return context
