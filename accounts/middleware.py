from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages

class LoginRequiredMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.user.is_authenticated:
            allowed_paths = [
                reverse('accounts:login'),
                reverse('accounts:register'),
                reverse('accounts:verify_otp'),
                reverse('home'),  # Add this line to allow access to the homepage
                # Add any other public URLs here
            ]
            if request.path not in allowed_paths:
                return redirect('accounts:login')
        return self.get_response(request)
