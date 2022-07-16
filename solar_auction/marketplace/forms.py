from django import forms
from . import models
from django.contrib.admin.widgets import AdminSplitDateTime


class CatalogueForm(forms.Form):
    name = forms.CharField(max_length=256, label='Name your catalogue ')
    details = forms.CharField(max_length=1024, label='Additional Details ')
    end_date = forms.SplitDateTimeField(
        label='End auction on ', widget=AdminSplitDateTime())
    starting_bid = forms.IntegerField(
        label='Start bidding from ', required=False)
    strategy_choices = (("ascending", 'low to high'),
                        ("descending", 'high to low'), ("quotes", 'get quotation'))
    strategy = forms.ChoiceField(
        choices=strategy_choices, widget=forms.Select())


class BidForm(forms.ModelForm):
    bid_amount = forms.IntegerField(label='New Bid Amount')

    class Meta:
        model = models.Bid
        fields = ('bid_amount',)
        labels = {
            'bid_amount': 'New Bid Amount'
        }


class CatalogueFileForm(forms.ModelForm):
    file_name = forms.FileField(
        label='Additional Details', required=False)

    class Meta:
        model = models.CatalogueFile
        fields = ('file_name',)

