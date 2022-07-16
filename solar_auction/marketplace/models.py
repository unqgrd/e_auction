from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.template.defaultfilters import slugify
import random
from django.utils import timezone
from auditlog.registry import auditlog


class Catalogue(models.Model):
    name = models.CharField(max_length=256)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    details = models.CharField(max_length=1024)
    end_date = models.DateTimeField()
    starting_bid = models.PositiveIntegerField(default=0)
    admin_approved = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, db_index=True)
    strategy_choices = (("ascending", 'low to high'),
                        ("descending", 'high to low'), ("quotes", 'get quotation'))
    strategy = models.CharField(max_length=10, choices=strategy_choices)
    broker_fees = models.FloatField(default=0)
    tech_specs = models.JSONField(blank=True, null=True)

    def auction_status(self):
        now = timezone.now()

        return now < self.end_date

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("catalogue_detail", kwargs={"slug": self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            slug_str = self.name + str(random.randint(1, 256))
            self.slug = slugify(slug_str)
        return super().save(*args, **kwargs)


class Bid(models.Model):
    catalogue_name = models.ForeignKey(Catalogue, on_delete=models.CASCADE)
    bid_amount = models.PositiveIntegerField()
    bidder = models.ForeignKey(User, on_delete=models.CASCADE)
    
    tech_specs = models.JSONField(null=True, blank=True)

    def __str__(self):
        return 'Bid amount '+str(self.bid_amount) + ' on ' + self.catalogue_name.name

    

class CatalogueFile(models.Model):
    catalogue_name = models.ForeignKey(Catalogue, on_delete=models.CASCADE)
    file_name = models.FileField(
        upload_to="catalogue_file", blank=True, null=True)


auditlog.register(Catalogue)
auditlog.register(Bid)
