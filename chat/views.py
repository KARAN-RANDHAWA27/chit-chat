from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q, Case, When, Value, CharField, Prefetch
from django.db.models.functions import Concat
from django.http import JsonResponse
from .models import Chat, Message
from django.contrib.auth import get_user_model
from .forms import GroupChatForm

User = get_user_model()

class ChatRoomListView(LoginRequiredMixin, ListView):
    template_name = 'chat/room_list.html'
    context_object_name = 'chats'

    def get_queryset(self):
        return Chat.objects.filter(participants=self.request.user).prefetch_related(
            Prefetch('participants', queryset=User.objects.exclude(id=self.request.user.id), to_attr='other_participants'),
            Prefetch('messages', queryset=Message.objects.order_by('-timestamp'), to_attr='last_messages')
        ).order_by('-last_message_time')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        for chat in context['chats']:
            if not chat.is_group_chat and chat.other_participants:
                chat.other_participant = chat.other_participants[0]
                chat.display_name = chat.other_participant.get_full_name() or chat.other_participant.username
            else:
                chat.display_name = chat.name
            chat.last_message = chat.last_messages[0] if chat.last_messages else None
        return context

class ChatRoomDetailView(LoginRequiredMixin, DetailView):
    template_name = 'chat/room_detail.html'
    context_object_name = 'chat'

    def get_queryset(self):
        return Chat.objects.filter(participants=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['messages'] = self.object.messages.order_by('timestamp')
        context['chats'] = Chat.objects.filter(participants=self.request.user).order_by('-last_message_time')
        
        for chat in context['chats']:
            if not chat.is_group_chat:
                chat.other_participant = chat.participants.exclude(id=self.request.user.id).first()
                chat.name = chat.other_participant.get_full_name() or "Chit Chat User"
            chat.last_message = chat.messages.order_by('-timestamp').first()

        if not self.object.is_group_chat:
            context['other_participant'] = self.object.participants.exclude(id=self.request.user.id).first()
            context['chat_name'] = context['other_participant'].get_full_name() or "Chit Chat User"
        else:
            context['chat_name'] = self.object.name
        
        return context

class CreateOneToOneChatView(LoginRequiredMixin, FormView):
    template_name = 'chat/create_one_to_one_chat.html'
    form_class = GroupChatForm
    success_url = reverse_lazy('chat:room_list')

    def form_valid(self, form):
        other_user = form.cleaned_data['participants'].first()
        existing_chat = Chat.objects.filter(
            participants=self.request.user
        ).filter(
            participants=other_user
        ).filter(
            is_group_chat=False
        ).first()

        if existing_chat:
            return redirect('chat:room_detail', pk=existing_chat.id)

        chat = Chat.objects.create(
            name=other_user.get_full_name() or other_user.username,
            is_group_chat=False
        )
        chat.participants.add(self.request.user, other_user)
        return super().form_valid(form)

class CreateGroupChatView(LoginRequiredMixin, FormView):
    template_name = 'chat/create_group_chat.html'
    form_class = GroupChatForm
    success_url = reverse_lazy('chat:room_list')

    def form_valid(self, form):
        chat = Chat.objects.create(
            name=form.cleaned_data['name'],
            is_group_chat=True
        )
        chat.participants.add(self.request.user, *form.cleaned_data['participants'])
        return super().form_valid(form)

def search_users(request):
    query = request.GET.get('q', '')
    users = User.objects.filter(
        Q(username__icontains=query) | Q(email__icontains=query)
    ).exclude(id=request.user.id)[:10]
    return JsonResponse(list(users.values('id', 'username', 'email')), safe=False)

class CreateChatView(LoginRequiredMixin, CreateView):
    model = Chat
    template_name = 'chat/create_chat.html'
    fields = []

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['users'] = User.objects.filter(is_active=True).exclude(id=self.request.user.id).annotate(
            display_name=Case(
                When(Q(first_name='') & Q(last_name=''), then=Value('ChitChat User')),
                default=Concat('first_name', Value(' '), 'last_name'),
                output_field=CharField()
            )
        ).values('id', 'display_name', 'email')
        return context

    def form_valid(self, form):
        participant_id = self.request.POST.get('participant')
        if participant_id:
            participant = User.objects.get(id=participant_id)
            existing_chat = Chat.objects.filter(
                participants=self.request.user
            ).filter(
                participants=participant
            ).filter(
                is_group_chat=False
            ).first()

            if existing_chat:
                return redirect('chat:room_detail', pk=existing_chat.id)

            chat = Chat.objects.create(
                name=participant.get_full_name() or participant.username,
                is_group_chat=False
            )
            chat.participants.add(self.request.user, participant)
            return redirect('chat:room_detail', pk=chat.id)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse_lazy('chat:room_detail', kwargs={'pk': self.object.id})

def test_websocket(request):
    return render(request, 'chat/test.html')