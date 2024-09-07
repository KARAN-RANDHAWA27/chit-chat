from django.urls import path
from .views import RegisterView, VerifyOTPView, CustomLoginView, LogoutView, ProfileView, SubmitTestimonialView

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify_otp'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),  # Make sure this line is present
    path('submit-testimonial/', SubmitTestimonialView.as_view(), name='submit_testimonial'),
]
