from django.db.models import Manager

import factory


from . import models

#todo test is not working afte generic relationship change

class BaseBoardsFactory(factory.DjangoModelFactory):
    class Meta:
        abstract = True

class BoardsFactory(factory.DjangoModelFactory):
    class Meta():
        model = models.Board
    name = factory.Faker("name")

    @factory.post_generation
    def fix_positions(self, create, extracted):
        self.fix_positions()

class BoardsFactoryWithSubBoard(factory.DjangoModelFactory):
    class Meta():
        model = models.Board
    name = factory.Faker("name")
    child = factory.RelatedFactoryList(factory=BoardsFactory, factory_related_name="parent", size=4)

    @factory.post_generation
    def fix_positions(self, create, extracted):
        self.fix_positions()

class BoardsGroupsFactory(factory.DjangoModelFactory):
    class Meta():
        model = models.BoardGroup
    name = factory.Faker("name")
    child = factory.RelatedFactoryList(factory=BoardsFactoryWithSubBoard, factory_related_name="parent", size=4)

    @factory.post_generation
    def fix_positions(self, create, extracted):
        self.fix_positions()


class BoardsFactoryPositionNone(BaseBoardsFactory):
    class Meta():
        model = models.Board
    position = None

    @factory.post_generation
    def fix_positions(self, create, extracted):
        self.fix_positions()

class BoardsGroupsFactoryBoardsPositionSetToNone(BaseBoardsFactory):
    class Meta():
        model = models.BoardGroup
    position = None
    child = factory.RelatedFactoryList(factory=BoardsFactoryPositionNone, factory_related_name="parent", size=4)

    @factory.post_generation
    def fix_positions(self, create, extracted):
        self.fix_positions()