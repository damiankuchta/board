from django import template

register = template.Library()

@register.simple_tag
def can_user_view_it(user, board):
    return board.can_user_view_it(user)