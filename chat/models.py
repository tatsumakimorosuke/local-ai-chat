
from django.db import models


class Conversation(models.Model):
    title = models.CharField(max_length=100, default="新しい会話")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Message(models.Model):
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages"
    )
    role = models.CharField(
        max_length=10,
        choices=[
            ("user", "User"),
            ("assistant", "Assistant"),
        ]
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content[:30]}"
