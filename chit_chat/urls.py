from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from accounts.views import HomePageView, TestimonialListCreateView, UserTestimonialListView, SubmitTestimonialView, LogoutView
from accounts.api_views import TokenObtainPairView, TokenRefreshView, CustomTokenObtainPairView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('chat/', include('chat.urls')),
    path('', HomePageView.as_view(), name='home'),
    path('api/testimonials/', TestimonialListCreateView.as_view(), name='testimonial-list-create'),
    path('api/testimonials/user/', UserTestimonialListView.as_view(), name='user-testimonial-list'),
    path('submit-testimonial/', SubmitTestimonialView.as_view(), name='submit_testimonial'),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('accounts/logout/', LogoutView.as_view(), name='logout'),  # This handles both API and web logout
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
