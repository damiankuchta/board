from django.views.generic import TemplateView
from django.shortcuts import get_list_or_404, get_object_or_404, redirect, render

from . import models

# todo if user is not allowed to go he wont
class BoardsGroup(TemplateView):
    template_name = "boards_app/boards_groups.html"

    def _get_board_groups_that_user_can_view(self):
        def get_board_groups():
            if 'board_group_id' in self.kwargs:
                return get_list_or_404(models.BoardGroup, id=self.kwargs['board_group_id'])
            else:
                return models.BoardGroup.objects.all()

        def get_user_can_view_board_groups(board_groups):
            user_can_view_board_groups = []
            for board_group in board_groups:
                if board_group.can_user_view_it(self.request.user):
                    user_can_view_board_groups.append(board_group)
            return user_can_view_board_groups

        board_groups = get_board_groups()
        return get_user_can_view_board_groups(board_groups)

    def get_context_data(self, **kwargs):
        context = super(BoardsGroup, self).get_context_data()
        context['board_groups'] = self._get_board_groups_that_user_can_view()
        return context


class Board(TemplateView):
    template_name = "boards_app/board.html"

    def _get_boards_that_user_can_view(self):
        board = get_object_or_404(models.Board, id=self.kwargs['board_id'])
        if board.can_user_view_it(self.request.user):
            return board
        else:
            return None

    def get_context_data(self, **kwargs):
        context = super(Board, self).get_context_data()
        context['board'] = self._get_boards_that_user_can_view()
        return context

    def dispatch(self, request, *args, **kwargs):
        context = self.get_context_data()
        if context['board'] is None:
            return redirect("index")
        else:
            return render(self.request, self.template_name, context=context)




