from django import template

register = template.Library()

@register.simple_tag
def can_user_add_new_psots(user, board):
    return board.can_user_add_new_posts(user)