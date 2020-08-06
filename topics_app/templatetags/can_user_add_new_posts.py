from django.template import Library

register = Library()

@register.simple_tag
def can_user_add_new_posts(topic, user):
    return topic.can_user_add_new_posts(user)