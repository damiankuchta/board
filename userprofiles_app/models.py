from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import send_mail


class User(AbstractUser):
    email = models.EmailField(unique=True)
    token_generator = PasswordResetTokenGenerator()

    def send_activation_emial(self, request):
        if not self.is_active:
            message = render_to_string("userprofiles_app/emials/email_activate_account.html",
                                       {"user": self.username,
                                        'domain': get_current_site(request).domain,
                                        "token": self.token_generator.make_token(self)})

            send_mail(subject="Welcome {user}".format(user=self.username),
                      message=strip_tags(message),
                      html_message=message,
                      from_email="Boards",
                      recipient_list=[self.email],
                      fail_silently=False)

    def get_all_warrnings(self):
        return self.reports_warrnings_bans_app_warrning.all()

    def get_all_bans(self):
        return self.reports_warrnings_bans_app_ban.filter(is_active=True)

    def get_all_posts(self):
        return self.post_set.filter(is_topic_post=False)

    def get_all_topics(self):
        topics = []
        for topic_post in self.post_set.filter(is_topic_post=True):
            topics.append(topic_post.topic)
        return topics

    def get_bans_count(self):
        return len(self.get_all_bans())

    def get_warrnings_count(self):
        return len(self.get_all_warrnings())

    def get_topics_count(self):
        return len(self.get_all_topics())

    def get_posts_count(self):
        return  len(self.get_all_posts())
