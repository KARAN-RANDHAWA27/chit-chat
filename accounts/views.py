from django.shortcuts import render, redirect
from django.views.generic import CreateView, UpdateView, TemplateView, FormView
from django.contrib.auth.views import LoginView
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.views import View
from django.contrib.auth import logout, login
from rest_framework import generics, permissions
from django.utils import timezone

from .forms import CustomUserCreationForm, CustomUserChangeForm, OTPVerificationForm, TestimonialForm
from .models import CustomUser, Testimonial
from .serializers import TestimonialSerializer
from .mixins import UserTestimonialMixin
from .utils import send_otp_email

# Create your views here.

class RegisterView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:verify_otp')

    def form_valid(self, form):
        user = form.save(commit=False)
        is_new_user = user.pk is None
        user.set_otp()
        user.email_verified = False  # Ensure email is not verified on registration/update
        user.save()
        
        if is_new_user:
            messages.success(self.request, "Your account has been created. Please verify your email.")
        else:
            messages.success(self.request, "Your account has been updated. Please verify your email.")
        
        send_otp_email(user)
        return super().form_valid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"{error}")
        return super().form_invalid(form)

class VerifyOTPView(FormView):
    template_name = 'accounts/verify_otp.html'
    form_class = OTPVerificationForm
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        otp = form.cleaned_data['otp']
        user = CustomUser.objects.filter(otp=otp, email_verified=False).first()
        if user and user.is_otp_valid():
            user.email_verified = True
            user.otp = None
            user.otp_created_at = None
            user.save()
            login(self.request, user)
            messages.success(self.request, 'Email verified successfully!')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Invalid or expired OTP. Please try again.')
            return self.form_invalid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Invalid OTP. Please try again.')
        return super().form_invalid(form)

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    
    def get_success_url(self):
        return reverse_lazy('home')  # or whatever your home page URL name is
    
    def form_valid(self, form):
        messages.success(self.request, f"Welcome back, {form.get_user().username}!")
        return super().form_valid(form)
    
    def form_invalid(self, form):
        email = form.cleaned_data.get('username')  # Assuming you're using email as username
        user_exists = CustomUser.objects.filter(email=email).exists()
        if not user_exists:
            messages.error(self.request, "This account doesn't exist. Please create an account.")
            return redirect('accounts:register')
        messages.error(self.request, "Invalid email or password. Please try again.")
        return super().form_invalid(form)

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')

class ProfileView(LoginRequiredMixin, UpdateView):
    model = CustomUser
    form_class = CustomUserChangeForm
    template_name = 'accounts/profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self, queryset=None):
        return self.request.user

    @transaction.atomic
    def form_valid(self, form):
        user = form.save(commit=False)
        email = form.cleaned_data['email']
        user.username = email
        user.email = email
        user.save()
        messages.success(self.request, 'Profile updated successfully!')
        return super().form_valid(form)



class HomePageView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['testimonials'] = Testimonial.objects.filter(is_approved=True).order_by('-created_at')[:2]
        return context

class SubmitTestimonialView(UserTestimonialMixin, CreateView):
    model = Testimonial
    form_class = TestimonialForm
    template_name = 'submit_testimonial.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class TestimonialListCreateView(generics.ListCreateAPIView):
    queryset = Testimonial.objects.filter(is_approved=True)
    serializer_class = TestimonialSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class UserTestimonialListView(generics.ListAPIView):
    serializer_class = TestimonialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Testimonial.objects.filter(user=self.request.user)
