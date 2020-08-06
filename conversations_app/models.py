from django.db import models
from userprofiles_app.models import User


class BaseConversationClass(models.Model):
    user = models.ForeignKey(User)
    created_datetime = models.DateTimeField(auto_now_add=True)


class Conversations(BaseConversationClass):
    title = models.CharField(max_length=124)
    users_in_conversation = models.ManyToManyField(User)


class Message(BaseConversationClass):
    message = models.TextField()
    conversation = models.ForeignKey(Conversations)
