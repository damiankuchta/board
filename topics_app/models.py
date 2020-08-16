from django.shortcuts import reverse
from django.db import models
from django.core.paginator import Paginator, InvalidPage
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError

from hitcount.models import HitCount, HitCountMixin

from boards_app.models import Board
from userprofiles_app.models import User


# custom exception for 'get_page_numbers_to_display'
class MustBeOddNumber(Exception):
    pass


class BaseTopicClass(models.Model):
    class Meta:
        abstract = True

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    creation_datetime = models.DateTimeField(auto_now_add=True)
    edited_datetime = models.DateTimeField(auto_now=True)
    times_edited = models.SmallIntegerField(null=True)


class Topic(BaseTopicClass, HitCountMixin):
    class Meta:
        ordering = ['last_post_datetime']

    title = models.CharField(max_length=124)

    last_post_datetime = models.DateTimeField(null=True, auto_now_add=True)
    is_closed = models.BooleanField(default=False)
    hit_count_generic = GenericRelation(HitCount, related_query_name="hit_count_generic_relation",
                               object_id_field="object_pk")

    board = models.ForeignKey(Board,
                              on_delete=models.SET_NULL,
                              related_name="topics",
                              null=True)

    def get_absolute_url(self):
        return reverse('topic', kwargs={"topic_id": self.id})

    def __str__(self):
        return self.title

    def get_posts(self):
        return self.post_set.all()

    def get_pagnatinated_posts(self):
        return Paginator(self.get_posts(), 10)

    def get_page(self, page):
        paginator = self.get_pagnatinated_posts()
        try:
            return paginator.page(page)
        except InvalidPage:
            return paginator.page(paginator.num_pages)

    def is_topic_closed(self):
        return self.is_closed

    def close_topic(self):
        self.is_closed = True

    def open_topic(self):
        self.is_closed = False

    def get_last_created_post(self):
        return self.post_set.latest("creation_datetime")

    def get_last_posted_user(self):
        try:
            return self.get_last_created_post().user
        except AttributeError:
            return self.user

    def get_last_post_datetime(self):
        try:
            last_post_datetime =  self.get_last_created_post().creation_datetime
        except AttributeError:
            last_post_datetime = self.creation_datetime
        return last_post_datetime.strftime('%d/%m/%y %H:%M')

    def get_amount_of_posts(self):
        return self.post_set.count()-1

    def is_topic_visible(self):
        topic_post = self.post_set.filter(is_topic_post=True).first()
        for ban in topic_post.reports_warrnings_bans_app_ban.all():
            if ban.is_ban_active() and ban.hide_related_object:
                return False
        return True

    def can_user_add_new_posts(self, user):
        if self.is_topic_closed():
            return False
        else:
            return self.board.can_user_add_new_posts(user)


# ------------------------------------------------------------------------------


class Post(BaseTopicClass):
    class Meta:
        ordering = ['creation_datetime']

    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, null=True)
    content = models.TextField()
    can_be_deleted = models.BooleanField(default=True)
    is_topic_post = models.BooleanField(default=False)

    def delete(self, using=None, keep_parents=False):
        if self.is_topic_post:
            self.topic.delete()
        if self.can_be_deleted:
            super(Post, self).delete(using, keep_parents)

    def get_absolute_url(self):
        return self.topic.get_absolute_url()

    def get_content(self):
        return self.content

    def is_post_first(self):
        return self.is_topic_post

    def clean(self):
        if self.topic:
            if self.topic.is_topic_closed():
                raise ValidationError()

    def get_all_warrnings(self):
        return self.reports_warrnings_bans_app_warrning.all()

    def get_all_bans(self):
        return self.reports_warrnings_bans_app_ban.all()

    def can_post_be_viewed(self):
        for warrning in self.get_all_warrnings():
            if warrning.hide_related_object:
                return False
        for ban in self.get_all_bans():
            if ban.hide_related_object:
                return False
        return True

    def get_ban_warrning_reason_to_display(self):
        messages = []
        for warrning in self.get_all_warrnings():
            if warrning.deisplay_reason_on_related_object:
                messages.append("Warrning: {}".format(warrning.reason))
        for ban in self.get_all_bans():
            if ban.deisplay_reason_on_related_object:
                messages.append("Ban: {}".format(ban.reason))
        return messages










