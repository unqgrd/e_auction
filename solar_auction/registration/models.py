from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from phonenumber_field.modelfields import PhoneNumberField
from auditlog.registry import auditlog
# Create your models here.

User._meta.get_field('email')._unique = True


class UserProfileInfo(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    verifying_token = models.CharField(
        max_length=64, blank=True, null=True, editable=False)
    admin_approved = models.BooleanField(default=False)
    name = models.CharField(max_length=256)
    phone = PhoneNumberField()

    address = models.CharField(max_length=2048, blank=True, null=True)
    city = models.CharField(max_length=128, blank=True, null=True)
    state = models.CharField(max_length=64, blank=True, null=True)
    country = models.CharField(max_length=64, blank=True, null=True)
    # registration_date = models.DateField()
    # account_activation_date = models.DateField()
    organization_name = models.CharField(max_length=512)
    # organization_type = models.TextChoices()
    organization_gstin = models.CharField(max_length=64, blank=True, null=True)
    organization_cin = models.CharField(max_length=64, blank=True, null=True)
    documents_uploaded = models.BooleanField(default=False, null=True)

    def __str__(self):
        return self.user.username


class Documents(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    proof_of_identity = models.FileField(upload_to='files/')
    proof_of_address = models.FileField(upload_to='files/')
    proof_of_gst = models.FileField(upload_to='files/')

    class Meta:
        verbose_name_plural = 'User Documents'

    def __str__(self):
        return self.user.username


auditlog.register(UserProfileInfo)
auditlog.register(Documents)
