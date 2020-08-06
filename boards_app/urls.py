from django.urls import path

from . import views

urlpatterns = [
    path("", views.BoardsGroup.as_view(), name="index"),
    path("boards/<int:board_group_id>/", views.BoardsGroup.as_view(), name="board_group"),
    path("boards/board/<int:board_id>/", views.Board.as_view(), name="board"),
]