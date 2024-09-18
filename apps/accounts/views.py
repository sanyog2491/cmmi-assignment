from django.contrib import messages
from allauth.account.views import LoginView,PasswordResetView,ResetPasswordForm

from django import forms
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.conf import settings
from django.core.mail import send_mail
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

User = get_user_model()

@method_decorator(csrf_exempt, name='dispatch')
class CustomLoginView(LoginView):
    template_name = 'custom_auth/login.html'  

class CustomPasswordResetForm(ResetPasswordForm):
    def clean_email(self):
        email = self.cleaned_data.get("email")
        # Check if the email exists in the User model
        if not User.objects.filter(email=email).exists():
            raise forms.ValidationError("Users with this email address do not exist.")
        return email

    def save(self, request, **kwargs):
        # Fetch users associated with the email
        email = self.cleaned_data["email"]
        users = User.objects.filter(email=email)

        if users.exists():
            for user in users:
                self.send_reset_email(user, request)

    def send_reset_email(self, user, request):
        """
        Custom method to handle sending the password reset email.
        """
        # Generate the token and uid
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))

        # Build the reset link
        reset_link = request.build_absolute_uri(
            reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        )

        # Prepare the context for rendering the email template
        context = {
            'user': user,
            'reset_link': reset_link,
        }

        # Use a template for the email content
        subject = "Password Reset Request"
        message = render_to_string('custom_auth/password_reset_email.html', context)

        # Send the email
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )


class CustomForgotPasswordView(PasswordResetView):
    template_name = 'custom_auth/forgotpassword.html'  
    
    def form_valid(self, form):
        form.save(self.request)
        messages.success(self.request, "We have sent you an email. If you have not received it please check your spam folder. Otherwise, contact us if you do not receive it in a few minutes.")
        return self.render_to_response(self.get_context_data(form=form))


    
@login_required
def dashboard_view(request):
    return render(request, 'custom_auth/dashboard.html')


