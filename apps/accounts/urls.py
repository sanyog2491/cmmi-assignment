from django.urls import path
from .views import CustomLoginView,custom_logout_view,UserView
from apps.accounts import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('accounts/login/', CustomLoginView.as_view(), name='account_login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('accounts/password/reset/',views.CustomForgotPasswordView.as_view(),name='forgotpassword'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('accounts/logout/', custom_logout_view, name='account_logout'), 
    path('api/users/', UserView.as_view(), name='user_list'), 
    path('api/users/<int:user_id>/', UserView.as_view(), name='user_detail'),  # Handles GET, PUT, PATCH, DELETE

]
