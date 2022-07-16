from django.urls import path
from . import views

app_name = 'administration'

urlpatterns = [
    path('', views.index, name='admin_index'),
    path('approved_users',
         views.ApprovedUsersView.as_view(), name='approved_users'),
    path('users_waiting', views.UnApprovedUsersView.as_view(), name='users_waiting'),
    path('documents_awaited', views.DocumentsUploadedView.as_view(),
         name='undocumented_users'),
    path('email_unverified', views.EmailUnverifiedView.as_view(),
         name='unverified_users'),
    path('approved_catalogue', views.ApprovedCatalogueView.as_view(),
         name='approved_catalogue'),
    path('catalogue_waiting', views.UnApprovedCatalogueView.as_view(),
         name='catalogue_waiting'),
    path('user_detail/<pk>',
         views.UserProfileView.as_view(), name='user_detail'),
    path('catalogue_detail/<slug>',
         views.AdminCatalogueView.as_view(), name='catalogue_detail'),
    path('catalogue_action/<slug>',
         views.catalogue_action, name='catalogue_action'),
    path('user_action/<pk>',
         views.user_action, name='user_action'),
    path('finished_auctions', views.AuctionOverView.as_view(),
         name='finished_auctions'),
    path('orders_list', views.OrdersView.as_view(),
         name='user_orders'),
    #     path('logs', views.LogsView.as_view(),
    #          name='audit_logs'),

]
