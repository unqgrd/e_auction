from django.urls import path
from . import views

app_name = 'marketplace'

urlpatterns = [
    path('', views.CatalogueListView.as_view(), name='all_catalogue'),
    path('marketplace_history', views.AuctionOverView.as_view(),
         name='history_catalogue'),
    path('detail/<slug:slug>/', views.CatalogueDetailView.as_view(),
         name='catalogue_detail'),
    path('user/catalogues/', views.UserCatalogueView.as_view(),
         name='user_catalogue'),
    path('user/bids/', views.UserBidView.as_view(), name='user_bids'),
    path('user/add_item', views.addItemView, name='add_item'),
    path('<slug>/add_bid/', views.addBidView, name='add_bid'),
    path('notify/<slug>', views.notify_winner, name='notify_winner'),
    path('search', views.SearchView.as_view(), name='search')
]
