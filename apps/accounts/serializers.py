from rest_framework import serializers
from django.contrib.auth.models import User
from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email

class RegisterSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return email

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        return data

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.validated_data
        user.email = self.cleaned_data.get('email')
        user.set_password(self.cleaned_data.get('password1'))
        user.save()
        setup_user_email(request, user, [])
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'
