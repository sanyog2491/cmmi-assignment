from django.urls import path
from .views import CustomLoginView
from apps.accounts import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('accounts/login/', CustomLoginView.as_view(), name='account_login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('accounts/password/reset/',views.CustomForgotPasswordView.as_view(),name='forgotpassword'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
]
