from django.db import models
from registration.models import UserProfileInfo
from marketplace.models import Catalogue
from auditlog.registry import auditlog
from .constants import PaymentStatus
# Create your models here.


class Order(models.Model):
    owner = models.ForeignKey(
        UserProfileInfo, on_delete=models.CASCADE, verbose_name="customer")
    catalogue = models.ForeignKey(Catalogue, on_delete=models.CASCADE)
    fee_amount = models.FloatField()
    payment_status = models.CharField(
        default=PaymentStatus.PENDING, max_length=100, blank=False, null=False,)
    order_id = models.CharField(max_length=100)
    payment_id = models.CharField(max_length=100)
    signature_id = models.CharField(max_length=100)

    def __str__(self):
        return str(self.owner) + ' on ' + str(self.catalogue) + ' ' + str(self.payment_status)


auditlog.register(Order)
