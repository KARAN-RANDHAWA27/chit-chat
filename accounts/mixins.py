from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Testimonial

class UserTestimonialMixin(LoginRequiredMixin):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_has_testimonial'] = Testimonial.objects.filter(user=self.request.user).exists()
        return context
