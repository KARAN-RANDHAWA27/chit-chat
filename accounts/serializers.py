from rest_framework import serializers
from .models import Testimonial
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

User = get_user_model()

class TestimonialSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Testimonial
        fields = ['id', 'user', 'content', 'created_at', 'is_approved']
        read_only_fields = ['is_approved']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Revoke all other tokens for this user
        RefreshToken.for_user(user)

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Update last login IP and user agent
        request = self.context['request']
        user = self.user
        user.last_login_ip = request.META.get('REMOTE_ADDR')
        user.last_login_user_agent = request.META.get('HTTP_USER_AGENT')
        user.save()

        return data
