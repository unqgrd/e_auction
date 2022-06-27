from django import forms
from django.contrib.auth.models import User
from .models import UserProfileInfo, Documents
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


def file_size(value):
    limit = 2 * 1024 * 1024
    if value.size > limit:
        raise ValidationError('File too large. Size should not exceed 2 MiB.')


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta():
        model = User
        fields = ('username', 'email', 'password', )

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)

        for fieldname in ['username', 'password', ]:
            self.fields[fieldname].help_text = None


class UserProfileInfoForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

    class Meta():
        model = UserProfileInfo
        fields = ('name', 'phone', 'address', 'city', 'state', 'country',)


class DocumentForm(forms.ModelForm):
    proof_of_identity = forms.FileField(
        label='Upload proof of identity', validators=[file_size])
    proof_of_address = forms.FileField(
        label='Upload proof of address', validators=[file_size])
    proof_of_gst = forms.FileField(
        label='Upload proof of GST number', validators=[file_size])

    class Meta:
        model = Documents
        fields = ('proof_of_identity', 'proof_of_address', 'proof_of_gst',)
