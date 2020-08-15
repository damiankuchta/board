from django.test import testcases
from django.contrib.auth.models import Group

from userprofiles_app.factory import GroupsFactory
from .test_factory import BoardsGroupsFactory,BoardsGroupsFactoryBoardsPositionSetToNone

from . import models


class TestBoard(testcases.TestCase):
    def setUp(self) -> None:

        GroupsFactory.reset_sequence()
        BoardsGroupsFactory.reset_sequence()

        GroupsFactory.create_batch(4)
        BoardsGroupsFactory.create_batch(2)

        self.RESTRICTION_GROUPS = ["visibility_groups", "new_topics_groups", "new_posts_groups"]

        self.board_group = models.BoardGroup.objects.get(id=1)
        self.groups = Group.objects.all()

        self.board_group.new_topics_groups.set(self.groups)
        self.board_group.new_posts_groups.set(self.groups)
        self.board_group.visibility_groups.set(self.groups)

        for child in self.board_group.child.all():
            child.new_posts_groups.set(self.groups)
            child.visibility_groups.set(self.groups)
            child.new_topics_groups.set(self.groups)

            for grand_child in child.child.all():
                grand_child.new_posts_groups.set(self.groups)
                grand_child.visibility_groups.set(self.groups)
                grand_child.new_topics_groups.set(self.groups)

        self.boards = []
        for x, group in enumerate(self.board_group.child.all().order_by("position")):
            self.boards.append(group)

        self.board_group_child = self.board_group.child.first()
        self.board_group_grand_child = self.board_group_child.child.first()

    # todo
    def test_view_func(self):
        pass

    def test_url(self):
        pass

    # make sure it deletes restriction group from its children as well
    def test_remove_groups_from_parent(self):
        def assert_that_all_groups_are_in_restricion_group(resitricion_group):
            self.assertTrue(all(item in self.groups for item in getattr(self.board_group, resitricion_group).all()))
            self.assertTrue(all(item in self.groups for item in getattr(self.board_group_child, resitricion_group).all()))
            self.assertTrue(all(item in self.groups for item in getattr(self.board_group_grand_child, resitricion_group).all()))

        def assert_that_deleted_group_is_not_in_resitriction_group(resitricion_group, deleted_group):
            self.assertFalse(deleted_group in getattr(self.board_group, resitricion_group).all())
            self.assertFalse(deleted_group in getattr(self.board_group_child, resitricion_group).all())
            self.assertFalse(deleted_group in getattr(self.board_group_grand_child, resitricion_group).all())

        def assert_that_remaing_groups_are_stil_in_resitricion_groups(resitricion_group, remaming_groups):
            self.assertTrue(all(item in remaming_groups for item in getattr(self.board_group, resitricion_group).all()))
            self.assertTrue(all(item in remaming_groups for item in getattr(self.board_group_child, resitricion_group).all()))
            self.assertTrue(all(item in remaming_groups for item in getattr(self.board_group_grand_child, resitricion_group).all()))

        def remove_group_from_restriction_grups(restriction_group, group):
            getattr(self.board_group, resitricion_group).remove(group)
            self.board_group.save()

        for resitricion_group in self.RESTRICTION_GROUPS:
            assert_that_all_groups_are_in_restricion_group(resitricion_group)

            deleted_group = self.groups[0]
            remiaing_groups = list(self.groups)
            remiaing_groups.remove(deleted_group)

            remove_group_from_restriction_grups(resitricion_group, deleted_group)

            assert_that_deleted_group_is_not_in_resitriction_group(resitricion_group, deleted_group)
            assert_that_remaing_groups_are_stil_in_resitricion_groups(resitricion_group, remiaing_groups)

    # on cleareance should not delete any groups from its child as it is set to none
    def test_set_parents_group_to_null(self):
        def remove_all_groups_from_resitrction_group(board, resitricion_group):
            getattr(board, resitricion_group).clear()

        def assert_restriction_group_does_not_have_any_groups(board, resitricion_group):
            self.assertFalse(getattr(board, resitricion_group).all())

        def assert_restriction_group_still_contains_given_group(board, resitricion_group):
            self.assertTrue(getattr(board, resitricion_group).all())

        for resitricion_group in self.RESTRICTION_GROUPS:
            remove_all_groups_from_resitrction_group(self.board_group, resitricion_group)

            assert_restriction_group_does_not_have_any_groups(self.board_group, resitricion_group)
            assert_restriction_group_still_contains_given_group(self.board_group_child, resitricion_group)
            assert_restriction_group_still_contains_given_group(self.board_group_grand_child, resitricion_group)

    # should delete all groups from its child except group [0]
    def test_parent_groups_are_null_then_set_it_to_group_zero(self):
        def remove_all_groups_from_resitrction_group(board, resitricion_group):
            getattr(board, resitricion_group).clear()

        def set_restriction_groups_to_given_group(parent, restriction,group):
            getattr(parent, restriction).set([group])

        def assert_group_stil_in_restriction_groups(group, restriction_group):
            self.assertTrue(group in getattr(self.board_group, restriction_group).all())
            self.assertTrue(group in getattr(self.board_group_child, restriction_group).all())
            self.assertTrue(group in getattr(self.board_group_grand_child, restriction_group).all())

        def assert_group_not_in_restriction_groups(group, restriction_group):
            self.assertFalse(group in getattr(self.board_group, restriction_group).all())
            self.assertFalse(group in getattr(self.board_group_child, restriction_group).all())
            self.assertFalse(group in getattr(self.board_group_grand_child, restriction_group).all())

        for resitricion_group in self.RESTRICTION_GROUPS:

            remove_all_groups_from_resitrction_group(self.board_group, resitricion_group)
            set_restriction_groups_to_given_group(self.board_group, resitricion_group, self.groups[0])

            assert_group_stil_in_restriction_groups(self.groups[0], resitricion_group)
            assert_group_not_in_restriction_groups(self.groups[1], resitricion_group)


    def test_can_user_assign_groups_that_should_not_be_able_to_assign(self):
        def remove_all_groups_from_resitrction_group(board, resitricion_group):
            getattr(board, resitricion_group).clear()

        def set_restriction_groups_to_given_group(parent, restriction, group):
            getattr(parent, restriction).set([group])

        def add_group_to_resitrcion_group(parent, restriction_group, group):
            getattr(parent, resitricion_group).add(group)

        for resitricion_group in self.RESTRICTION_GROUPS:
            remove_all_groups_from_resitrction_group(self.board_group, resitricion_group)

            set_restriction_groups_to_given_group(self.board_group, resitricion_group, self.groups[0])
            add_group_to_resitrcion_group(self.board_group_child, resitricion_group, self.groups[1])

            # assert that group 0 and its children contains group 0
            self.assertTrue(self.groups[0] in getattr(self.board_group, resitricion_group).all())
            self.assertTrue(self.groups[0] in getattr(self.board_group_child, resitricion_group).all())
            self.assertTrue(self.groups[0] in getattr(self.board_group_grand_child, resitricion_group).all())

            # assert that group 1 is not in any groups even though it was added to child
            self.assertFalse(self.groups[1] in getattr(self.board_group, resitricion_group).all())
            self.assertFalse(self.groups[1] in getattr(self.board_group_child, resitricion_group).all())
            self.assertFalse(self.groups[1] in getattr(self.board_group_grand_child, resitricion_group).all())

    def test_position_is_changed_to_none(self):
        def change_position_to_none(board):
            board.position = None
            board.save(update_fields=['position'])
            board.refresh_from_db()

        def check_if_position_is_last(board, parent):
            self.assertEqual(board.position, parent.child.count())

        def check_if_positions_are_in_order(parent):
            for x, board in enumerate(parent.child.order_by('position')):
                self.assertEqual(board.position, x + 1)

        change_position_to_none(self.boards[0])
        check_if_position_is_last(self.boards[0], self.board_group)
        check_if_positions_are_in_order(parent=self.board_group)

    def test_position_is_set_to_none_on_creation(self):
        boards_group_none = BoardsGroupsFactoryBoardsPositionSetToNone()

        for x, board in enumerate(boards_group_none.child.order_by('position')):
            self.assertEqual(board.position, x+1)

    def test_position_on_parent_change(self):
        board_group_two = models.BoardGroup.objects.get(id=2)

        self.boards[0].parent = board_group_two
        self.boards[0].save()

        self.assertEqual(self.boards[0].position, len(board_group_two.child.all()))

        for x, board in enumerate(self.board_group.child.order_by("position")):
            self.assertEqual(board.position, x+1)

        for x, board in enumerate(board_group_two.child.order_by("position")):
            self.assertEqual(board.position, x+1)

    def test_change_position_over_limit(self):
        self.boards[0].position = 10
        self.boards[0].save()

        self.assertEqual(self.boards[0].position, len(self.board_group.child.all()))

        for x, board in enumerate(self.board_group.child.order_by("position")):
            self.assertEqual(board.position, x + 1)

    def test_change_position_to_under_minimal(self):
        self.boards[0].position = -10
        self.boards[0].save()

        self.assertEqual(self.boards[0].position, 1)

        for x, board in enumerate(self.board_group.child.order_by("position")):
            self.assertEqual(board.position, x + 1)

    def test_change_position(self):
        self.boards[0].position = 3
        self.boards[0].save()

        self.assertEqual(self.boards[0].position, 3)

        for x, board in enumerate(self.board_group.child.order_by("position")):
            self.assertEqual(board.position, x + 1)

    def test_does_boards_position_change_affect_boards_with_didferent_parent(self):
        board_group_two = models.BoardGroup.objects.get(id=2)
        positions_list = []

        # get positions
        for child in board_group_two.child.order_by("position"):
            positions_list.append(child.position)

        # mess around with positions
        self.boards[0].position = 3
        self.boards[1].position = 2
        self.boards[2].position = 5
        self.boards[3].position = 1
        self.boards[0].save()
        self.boards[1].save()
        self.boards[2].save()
        self.boards[3].save()

        # check i old possitions are still the same
        for x, child in enumerate(board_group_two.child.order_by("position")):
            self.assertEqual(positions_list[x], child.position)


