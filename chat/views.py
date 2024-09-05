from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class RoomListView(TemplateView):
    template_name = 'chat/room_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # We'll add chat rooms to the context later
        return context
