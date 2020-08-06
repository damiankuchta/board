from django.views.generic import TemplateView
from django.shortcuts import get_list_or_404, get_object_or_404

from . import models


class BoardsGroup(TemplateView):
    template_name = "boards_app/boards_groups.html"

    def get_context_data(self, **kwargs):
        context = super(BoardsGroup, self).get_context_data()
        if 'board_group_id' in self.kwargs:
            context['board_groups'] = get_list_or_404(models.BoardGroup, id=self.kwargs['board_group_id'])
        else:
            context['board_groups'] = models.BoardGroup.objects.all()
        return context


class Board(TemplateView):
    template_name = "boards_app/board.html"

    def get_context_data(self, **kwargs):
        context = super(Board, self).get_context_data()
        if 'board_id' in self.kwargs:
            context['board'] = get_object_or_404(models.Board, id=self.kwargs['board_id'])
        else:
            context['board'] = models.BoardGroup.objects.all()
        return context



