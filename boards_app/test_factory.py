from enum import Enum
import factory

from . import models
#todo test is not working afte generic relationship change

class BaseBoardsFactory(factory.DjangoModelFactory):
    class Meta:
        abstract = True
    visibility = models.BaseBoardClass.RestrictionChoices['ALL']
    add_new_topics_restrictions = models.BaseBoardClass.RestrictionChoices['ALL']
    add_new_posts_restictions = models.BaseBoardClass.RestrictionChoices['ALL']

    name = factory.Faker("name")

    @factory.post_generation
    def fix_positions(self, create, extracted):
        self.fix_positions()

class BoardsFactory(BaseBoardsFactory):
    class Meta():
        model = models.Board


class BoardsFactoryWithSubBoard(BaseBoardsFactory):
    class Meta():
        model = models.Board
    child = factory.RelatedFactoryList(factory=BoardsFactory, factory_related_name="parent", size=4)


class BoardsGroupsFactory(factory.DjangoModelFactory):
    class Meta():
        model = models.BoardGroup
    child = factory.RelatedFactoryList(factory=BoardsFactoryWithSubBoard, factory_related_name="parent", size=4)


class BoardsFactoryPositionNone(BaseBoardsFactory):
    class Meta():
        model = models.Board
    position = None


class BoardsGroupsFactoryBoardsPositionSetToNone(BaseBoardsFactory):
    class Meta():
        model = models.BoardGroup
    position = None
    child = factory.RelatedFactoryList(factory=BoardsFactoryPositionNone, factory_related_name="parent", size=4)
