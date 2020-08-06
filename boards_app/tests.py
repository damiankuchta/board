from django.test import testcases
from django.db.models.signals import m2m_changed
import factory

from userprofiles_app.factory import GroupsFactory
from .test_factory import BoardsGroupsFactory, BoardsGroupsFactoryBoardsPositionSetToNone, SubBoardFactory
from . import signals
from . import models


def disconnect_signals():
    m2m_changed.disconnect(signals.can_add_posts_changed,
                           sender=models.BoardGroup.can_add_new_posts.through)
    m2m_changed.disconnect(signals.can_add_posts_changed,
                           sender=models.Board.can_add_new_posts.through)
    m2m_changed.disconnect(signals.can_view_changed,
                           sender=models.BoardGroup.can_view_group.through)
    m2m_changed.disconnect(signals.can_view_changed,
                           sender=models.Board.can_view_group.through)


def connect_signals():
    m2m_changed.connect(signals.can_add_posts_changed,
                        sender=models.BoardGroup.can_add_new_posts.through)
    m2m_changed.connect(signals.can_add_posts_changed,
                        sender=models.Board.can_add_new_posts.through)
    m2m_changed.connect(signals.can_view_changed,
                        sender=models.BoardGroup.can_view_group.through)
    m2m_changed.connect(signals.can_view_changed,
                        sender=models.Board.can_view_group.through)


class TestBoard(testcases.TestCase):
    def setUp(self) -> None:

        disconnect_signals()

        BoardsGroupsFactory.reset_sequence()
        GroupsFactory.reset_sequence()
        SubBoardFactory.reset_sequence()

        self.groups = []
        self.groups.extend(GroupsFactory.create_batch(4))

        self.board_group = []
        self.board_group.extend(BoardsGroupsFactory.create_batch(2))

        self.board_group[0].can_add_new_posts.set(self.groups)
        self.board_group[0].can_view_group.set(self.groups)

        for child in self.board_group[0].child.all():
            child.can_add_new_posts.set(self.groups)
            child.can_view_group.set(self.groups)

            for grand_child in child.child.all():
                grand_child.can_add_new_posts.set(self.groups)
                grand_child.can_view_group.set(self.groups)

        self.boards = []
        for x, group in enumerate(self.board_group[0].child.all().order_by("position")):
            self.boards.append(group)




        connect_signals()

    #todo
    def test_view_func(self):
        pass

    def test_url(self):
        pass


    def test_remove_can_view_groups_from_parent(self):

        board_group_child = self.board_group[0].child.all().first()
        board_group_grand_child = self.board_group[0].child.all().first().child.all().first()

        self.assertTrue(self.groups[0] in list(self.board_group[0].can_view_group.all()))
        self.assertTrue(self.groups[0] in list(board_group_child.can_view_group.all()))
        self.assertTrue(self.groups[0] in list(board_group_grand_child.can_view_group.all()))

        self.board_group[0].can_view_group.remove(self.groups[0])
        self.board_group[0].save()

        self.assertFalse(self.groups[0] in list(self.board_group[0].can_view_group.all()))
        self.assertFalse(self.groups[0] in list(board_group_child.can_view_group.all()))
        self.assertFalse(self.groups[0] in list(board_group_grand_child.can_view_group.all()))

        self.assertTrue(self.groups[1] in list(self.board_group[0].can_view_group.all()))
        self.assertTrue(self.groups[1] in list(board_group_child.can_view_group.all()))
        self.assertTrue(self.groups[1] in list(board_group_grand_child.can_view_group.all()))

    def test_add_groups_to_child_when_parent_restrictions_is_set_to_null(self):

        self.board_group[0].can_add_new_posts.clear()
        self.board_group[0].can_view_group.clear()

        for child in self.board_group[0].child.all():
            child.can_add_new_posts.set([self.groups[0], self.groups[1]])
            child.can_view_group.set([self.groups[0], self.groups[1]])

            for grand_child in child.child.all():
                grand_child.can_add_new_posts.set([self.groups[0], self.groups[1]])
                grand_child.can_view_group.set([self.groups[0], self.groups[1]])

        board_group_child = self.board_group[0].child.all().first()
        board_group_grand_child = self.board_group[0].child.all().first().child.all().first()

        self.assertFalse(self.board_group[0].can_add_new_posts.all())
        self.assertTrue(self.groups[0] in list(board_group_child.can_view_group.all()))
        self.assertTrue(self.groups[0] in list(board_group_grand_child.can_view_group.all()))

        self.board_group[0].can_add_new_posts.set([self.groups[0]])
        self.board_group[0].can_view_group.set([self.groups[0]])

        self.assertTrue(self.groups[0] in list(self.board_group[0].can_view_group.all()))
        self.assertTrue(self.groups[0] in list(board_group_child.can_view_group.all()))
        self.assertTrue(self.groups[0] in list(board_group_grand_child.can_view_group.all()))

        self.assertFalse(self.groups[1] in list(self.board_group[0].can_view_group.all()))
        self.assertFalse(self.groups[1] in list(board_group_child.can_view_group.all()))
        self.assertFalse(self.groups[1] in list(board_group_grand_child.can_view_group.all()))


    def test_take_away_all_groups_from_parent(self):

        board_group_child = self.board_group[0].child.all().first()
        board_group_grand_child = self.board_group[0].child.all().first().child.all().first()

        self.board_group[0].can_add_new_posts.remove(self.groups[0])
        self.assertFalse(self.groups[0] in list(self.board_group[0].can_add_new_posts.all()))

        self.board_group[0].can_add_new_posts.clear()

        self.assertFalse(self.groups[0] in list(self.board_group[0].can_add_new_posts.all()))
        self.assertFalse(self.groups[0] in list(board_group_child.can_add_new_posts.all()))
        self.assertFalse(self.groups[0] in list(board_group_grand_child.can_add_new_posts.all()))

        for x in range(1,3):
            self.assertFalse(self.groups[x] in list(self.board_group[0].can_add_new_posts.all()))
            self.assertTrue(self.groups[x] in list(board_group_child.can_add_new_posts.all()))
            self.assertTrue(self.groups[x] in list(board_group_grand_child.can_add_new_posts.all()))

    #todo
    def test_does_boards_position_change_affect_boards_with_didferent_parent(self):
        pass


    def test_position_is_changed_to_none(self):
        self.boards[0].position = None
        self.boards[0].save()
        self.boards[0].refresh_from_db()

        self.assertEqual(self.boards[0].position, self.board_group[0].child.count())

        for x, board in enumerate(self.board_group[0].child.all().order_by('position')):
            self.assertEqual(board.position, x+1)


    def test_position_is_set_to_none_on_creation(self):
        boards_group_none = BoardsGroupsFactoryBoardsPositionSetToNone()

        for x, board in enumerate(boards_group_none.child.all().order_by('position')):
            self.assertEqual(board.position, x+1)


    def test_position_on_parent_change(self):
        self.boards[0].parent = self.board_group[1]
        self.boards[0].save()

        self.assertEqual(self.boards[0].position, models.Board.objects.filter(parent=self.board_group[1])
                                          .count())

        for x, board in enumerate(models.Board.objects.filter(parent=self.board_group[1])
                                          .order_by('position').all()):
            self.assertEqual(board.position, x+1)


        for x, board in enumerate(models.Board.objects.filter(parent=self.board_group[0])
                                          .order_by('position').all()):
            self.assertEqual(board.position, x+1)


    def test_position_change_boards(self):
        def refresh_boards_from_db(boards):
            for board in boards:
                board.refresh_from_db()
            return boards

        self.boards[0].position = 10
        self.boards[0].save()
        self.boards = refresh_boards_from_db(self.boards)

        self.assertTrue(self.boards[1].position == 1)
        self.assertTrue(self.boards[2].position == 2)
        self.assertTrue(self.boards[3].position == 3)
        self.assertTrue(self.boards[0].position == 4)

        self.boards[1].position = 3
        self.boards[1].save()
        self.boards = refresh_boards_from_db(self.boards)

        self.assertTrue(self.boards[1].position == 3)
        self.assertTrue(self.boards[2].position == 1)
        self.assertTrue(self.boards[3].position == 2)
        self.assertTrue(self.boards[0].position == 4)

        self.boards[3].position = 1
        self.boards[3].save()
        refresh_boards_from_db(self.boards)
        self.assertTrue(self.boards[1].position == 3)
        self.assertTrue(self.boards[2].position == 2)
        self.assertTrue(self.boards[3].position == 1)
        self.assertTrue(self.boards[0].position == 4)

        self.boards[0].position = -10
        self.boards[0].save()
        refresh_boards_from_db(self.boards)
        self.assertTrue(self.boards[1].position == 4)
        self.assertTrue(self.boards[2].position == 3)
        self.assertTrue(self.boards[3].position == 2)
        self.assertTrue(self.boards[0].position == 1)

        self.boards[0].position = -10
        self.boards[0].save()
        refresh_boards_from_db(self.boards)
        self.assertTrue(self.boards[1].position == 4)
        self.assertTrue(self.boards[2].position == 3)
        self.assertTrue(self.boards[3].position == 2)
        self.assertTrue(self.boards[0].position == 1)