from django.db.models import Manager

import factory


from . import models

#todo test is not working afte generic relationship change

class BaseBoardsFactory(factory.DjangoModelFactory):
    class Meta:
        abstract = True

    position = factory.sequence(lambda x: x)
    name = factory.sequence(lambda x: "Test {board_number}".format(board_number=x))


class SubBoardFactory(BaseBoardsFactory):
    class Meta():
        model = models.Board


class BoardsFactory(BaseBoardsFactory):
    class Meta():
        model = models.Board


class BoardsGroupsFactory(BaseBoardsFactory):
    class Meta():
        model = models.BoardGroup

    child = factory.RelatedFactoryList(factory=BoardsFactory,
                                        factory_related_name="parent",
                                        size=4)


class BoardsFactoryPositionNone(BaseBoardsFactory):

    child = factory.RelatedFactoryList(factory=SubBoardFactory,
                                        factory_related_name="parent",
                                        size=2)
    position = None
    class Meta():
        model = models.Board

class BoardsGroupsFactoryBoardsPositionSetToNone(BaseBoardsFactory):
    class Meta():
        model = models.BoardGroup

    child = factory.RelatedFactoryList(factory=BoardsFactoryPositionNone,
                                       factory_related_name="parent",
                                       size=4)
