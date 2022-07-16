from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.utils.decorators import method_decorator
from registration.models import UserProfileInfo, Documents
from .forms import UserForm, UserProfileInfoForm, DocumentForm
from django.views.generic import View, DetailView, UpdateView
from solar_auction.settings import EMAIL_HOST_USER
from django.core.mail import send_mail
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.contrib.auth.views import PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages

import random


def verification_email_sender(site, email):

    mail_subject = 'Activation link for Uniqgrid E Auction'
    token = str(random.random()).split('.')[1]

    link = f'http://{site}/verify/{token}'
    message = 'Please click on '+link+' to confirm your account.'
    send_mail(mail_subject, message, EMAIL_HOST_USER,
              [email], fail_silently=False)
    return token
# Create your views here.


def index(request):
    try:
        user_profile = UserProfileInfo.objects.get(pk=request.user.id)
        user_status = User.objects.get(pk=request.user.id).is_staff

    except:
        user_profile = {}
    if user_profile:
        if user_status:
            return HttpResponseRedirect(reverse('administration:admin_index'))
        else:
            return HttpResponseRedirect(reverse('registration:profile_view'))
    else:
        return HttpResponseRedirect(reverse('registration:user_login'))


def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(data=request.POST)
        profile_form = UserProfileInfoForm(data=request.POST)

        if user_form.is_valid() and profile_form.is_valid():

            user = user_form.save(commit=False)
            user.is_active = False
            user.set_password(user.password)
            user.save()
            profile = profile_form.save(commit=False)
            profile.user = user
            profile.save()
            registered = True

            current_site = get_current_site(request)
            to_email = user_form.cleaned_data.get('email')

            profile.verifying_token = verification_email_sender(
                current_site, to_email)
            profile.save()

        else:
            print(user_form.errors, profile_form.errors)

    else:
        user_form = UserForm()
        profile_form = UserProfileInfoForm()

    return render(request, 'registration/registration.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'registered': registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('registration:index'))
            else:
                return HttpResponse('Account inactive')
        else:
            messages.info(
                request, 'Invalid details!')
            return render(request, 'registration/login.html')

    else:
        return render(request, 'registration/login.html')


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('registration:index'))


@method_decorator(login_required, name='dispatch')
class UserProfileView(DetailView):
    model = UserProfileInfo
    template_name = 'registration/my_profile.html'
    context_object_name = 'userprofile'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_user = UserProfileInfo.objects.get(user=self.request.user)
        context['user_profile'] = current_user

        return context

    def get_object(self, *args, **kwargs):
        return UserProfileInfo.objects.get(user=self.request.user)


@method_decorator(login_required, name='dispatch')
class UserUpdateView(View):
    def get(self, request):
        existing_detail = UserProfileInfo.objects.get(pk=self.request.user.id)
        form = UserProfileInfoForm(instance=existing_detail)
        current_user = UserProfileInfo.objects.get(user=self.request.user)
        return render(request, 'registration/edit_profile.html', {'form': form, 'user_profile': current_user})

    def post(self, request):
        existing_detail = UserProfileInfo.objects.get(pk=self.request.user.id)
        form = UserProfileInfoForm(request.POST, instance=existing_detail)
        current_user = UserProfileInfo.objects.get(user=self.request.user)
        if form.is_valid():
            # print('form_valid')
            form.save()
            # print('here')
            return HttpResponseRedirect(reverse('registration:profile_view'))
        return render(request, 'registration/edit_profile.html', {'form': form, 'user_profile': current_user})

    def get_object(self, *args, **kwargs):
        return UserProfileInfo.objects.get(user=self.request.user)


def verify_email(request, token):
    try:
        current_user = UserProfileInfo.objects.get(verifying_token=token)

        if current_user:

            current_user.user.is_active = True

            current_user.user.save()

            return render(request, 'registration/login.html')
    except:
        return HttpResponse('Invalid token')


def resend_email(request):
    if request.method == 'POST':
        requesting_email = request.POST.get('email')
        posted = True
        try:
            current_user = User.objects.get(email=requesting_email)
            message = 'Email has been sent. Please check your spam folders as well.'
            user_exists = True
            current_user_profile = UserProfileInfo.objects.get(
                user=current_user)
            current_site = get_current_site(request)
            current_user_profile.verifying_token = verification_email_sender(
                current_site, requesting_email)
            current_user_profile.save()

        except:
            message = 'No such email exits. Please register to continue.'
            user_exists = False
        return render(request, 'registration/email_reverification.html', {'message': message, 'user_exists': user_exists, 'posted': posted})
    else:
        message = 'Please enter the email id.'
        posted = False
        return render(request, 'registration/email_reverification.html', {'message': message, 'posted': posted})


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'registration/password_reset.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'

    success_url = reverse_lazy('registration:index')


class DocumentsUploadView(View):
    def get(self, request):
        current_user = User.objects.get(pk=self.request.user.id)
        current_user_profile = UserProfileInfo.objects.get(user=current_user)
        form = DocumentForm()

        return render(request, 'registration/documents_upload.html', {'form': form, 'user_profile': current_user_profile})

    def post(self, request):
        current_user = User.objects.get(pk=self.request.user.id)
        current_user_profile = UserProfileInfo.objects.get(user=current_user)
        form = DocumentForm(request.POST, request.FILES)

        if form.is_valid():
            documents = Documents(
                user=current_user, proof_of_identity=request.FILES['proof_of_identity'], proof_of_address=request.FILES['proof_of_address'], proof_of_gst=request.FILES['proof_of_gst'])
            documents.save()
            current_user_profile.documents_uploaded = True
            current_user_profile.save()
            return HttpResponseRedirect(reverse('registration:index'))
        return render(request, 'registration/documents_upload.html', {'form': form})
