import factory
from . import models
from boards_app import models as boards_models
from boards_app.test_factory import BaseBoardsFactory


class PostFactory(factory.DjangoModelFactory):
    class Meta():
        model = models.Post

    can_be_deleted = True


class TopicFactory(factory.DjangoModelFactory):
    class Meta():
        model = models.Topic

    post = factory.RelatedFactoryList(PostFactory, size=5, factory_related_name="topic")
    title = factory.Faker("company")
    is_closed = False

    @factory.PostGeneration
    def set_first_post_as_topic_post(self, create, extracted):
        first_post = self.post_set.order_by('creation_datetime').first()
        first_post.is_topic_post = True
        first_post.save()


class BoardFactory(BaseBoardsFactory):
    class Meta():
        model = boards_models.Board

    topics = factory.RelatedFactoryList(TopicFactory, size=4, factory_related_name="board")


class BoardGroupsFactory(BaseBoardsFactory):
    class Meta():
        model = boards_models.BoardGroup

    child = factory.RelatedFactory(BoardFactory, factory_related_name="parent")




