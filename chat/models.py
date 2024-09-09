from django.db import models
from django.conf import settings
from django.utils import timezone

class Chat(models.Model):
    name = models.CharField(max_length=255, null=True, blank=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)
    last_message_time = models.DateTimeField(null=True, blank=True)
    is_group_chat = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Chat'
        verbose_name_plural = 'Chats'
        ordering = ['-last_message_time']

    def __str__(self):
        return self.name or f"Chat {self.id}"

    def save_message(self, sender, content):
        message = Message.objects.create(chat=self, sender=sender, content=content)
        self.last_message_time = timezone.now()
        self.save(update_fields=['last_message_time'])
        return message

class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['timestamp']

    def __str__(self):
        return f"Message from {self.sender} in {self.chat}"
