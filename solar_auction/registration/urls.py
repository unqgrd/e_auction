from django.urls import path
from . import views

app_name = 'registration'

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('user_login', views.user_login, name='user_login'),
    path('user/<pk>', views.UserProfileView.as_view(), name='profile_view'),
    path('user/<pk>/edit', views.UserUpdateView.as_view(), name='user_update'),
    path('verify/<str:token>',
         views.verify_email, name='verify_email'),
    path('resend_email',
         views.resend_email, name='resend_email'),
    path('user/<pk>/documents', views.DocumentsUploadView.as_view(),
         name='upload_document'),

]
