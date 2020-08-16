from django.test import TestCase, Client
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import reverse

from . import test_factory
from . import models
from boards_app.models import BaseBoardClass
from boards_app.test_factory import BoardsGroupsFactory
from userprofiles_app.factory import UserFactory


class TopicTest(TestCase):
    def setUp(self) -> None:
        self.board_group = test_factory.BoardGroupsFactory.create()

        self.board = self.board_group.child.first()
        self.topic = self.board.topics.first()

    def test_get_last_created_post(self):
        last_post = self.topic.post_set.order_by('creation_datetime').last()
        self.assertEqual(self.topic.get_last_created_post(), last_post)

    def test_get_last_post_datetime(self):
        last_post = self.topic.post_set.order_by('creation_datetime').last()
        last_date_time = last_post.creation_datetime.strftime('%d/%m/%y %H:%M')
        self.assertEqual(self.topic.get_last_post_datetime(), last_date_time)

    def test_get_amount_of_posts(self):
        amount = self.topic.get_amount_of_posts()
        self.assertEqual(4, amount)

        post = self.topic.post_set.last()
        post.delete()

        self.topic.refresh_from_db()

        amount = self.topic.get_amount_of_posts()
        self.assertEqual(3, amount)




class NewTopicView(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = UserFactory(is_active=True)
        self.client.force_login(self.user)

        self.board_group = BoardsGroupsFactory.create()
        self.board = self.board_group.child.first()

    def test_create_new_topic_user_not_authorizated(self):
        self.board.add_new_topics_restrictions = BaseBoardClass.RestrictionChoices['NONE']
        self.board.save()

        self.assertFalse(models.Topic.objects.all())
        self.assertFalse(models.Post.objects.all())
        data = {"title": "Random Title",
                "content": "Random Conent"}
        self.client.post(reverse("add_new_topic", kwargs={"board_id": self.board.id}), data=data)
        self.assertFalse(models.Topic.objects.all())
        self.assertFalse(models.Post.objects.all())

    def test_create_new_topic(self):
        self.assertFalse(models.Topic.objects.all())
        self.assertFalse(models.Post.objects.all())
        data = {"title": "Random Title",
                "content": "Random Conent"}
        self.client.post(reverse("add_new_topic", kwargs={"board_id": self.board.id}), data=data)
        self.assertTrue(models.Topic.objects.all())
        self.assertTrue(models.Post.objects.all())


class NewPostView(TestCase):
    def setUp(self) -> None:
        self.client = Client()
        self.user = UserFactory(is_active=True)
        self.client.force_login(self.user)

        self.board_group = test_factory.BoardGroupsFactory.create()
        self.board = self.board_group.child.first()
        self.topic = self.board.topics.first()
        self.posts = self.topic.post_set.all()

    def test_add_new_post(self):
        data = {"content": "random content"}
        post_count = self.topic.get_amount_of_posts()
        self.client.post(reverse("topic", kwargs={"topic_id": self.topic.id}), data=data)
        new_post_count = self.topic.get_amount_of_posts()
        self.assertEqual(post_count+1, new_post_count)

    def test_can_user_add_new_post_to_closed_topic(self):
        self.topic.is_closed = True
        self.topic.save()
        post_count = self.topic.get_amount_of_posts()
        data = {"content": "random content"}
        self.client.post(reverse("topic", kwargs={"topic_id": self.topic.id}), data=data)
        new_post_count = self.topic.get_amount_of_posts()
        self.assertEqual(post_count, new_post_count)

    def test_delete_post(self):
        post_count = self.topic.get_amount_of_posts()
        self.posts[1].delete()
        new_post_count = self.topic.get_amount_of_posts()
        self.assertEqual(post_count-1, new_post_count)

    def test_delete_post_that_is_not_allowed_to_be_deleted(self):
        self.post = models.Post.objects.get(id=self.posts[1].id)
        self.post.can_be_deleted = False
        self.post.save()
        post_count = self.topic.get_amount_of_posts()
        self.post.delete()
        new_post_count = self.topic.get_amount_of_posts()
        self.assertEqual(post_count, new_post_count)

    def test_post_topic_gets_deleted(self):
        post_topic = self.topic.post_set.order_by("creation_datetime").first()
        self.assertTrue(post_topic.is_topic_post)
        post_topic.delete()

        try:
            self.topic.refresh_from_db()
        except ObjectDoesNotExist:
            self.assertTrue(True)
        else:
            self.assertTrue(False)
