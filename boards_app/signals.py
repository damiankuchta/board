from django.db.models.signals import m2m_changed, pre_save, post_save
from django.dispatch import receiver

from . import models

"""On Group/Board group restrictions change,
it deletes from related Boards groups all Groups that are not in the Group/Board groups"""

@receiver(m2m_changed, sender=models.BoardGroup.new_topics_groups.through)
@receiver(m2m_changed, sender=models.Board.new_posts_groups.through)
def can_add_posts_changed(instance, pk_set, action, sender, **kwargs):
    instance.update_restrictions_groups(pk_set=pk_set,
                                        action=action,
                                        group="new_topics_groups",
                                        instance=instance)

@receiver(m2m_changed, sender=models.Board.visibility_groups.through)
@receiver(m2m_changed, sender=models.BoardGroup.visibility_groups.through)
def can_view_changed(instance, pk_set, action, **kwargs):
    instance.update_restrictions_groups(pk_set=pk_set,
                                        action=action,
                                        group="visibility_groups",
                                        instance=instance)

@receiver(m2m_changed, sender=models.Board.new_posts_groups.through)
@receiver(m2m_changed, sender=models.BoardGroup.new_posts_groups.through)
def can_view_changed(instance, pk_set, action, **kwargs):
    instance.update_restrictions_groups(pk_set=pk_set,
                                        action=action,
                                        group="new_posts_groups",
                                        instance=instance)


@receiver(pre_save, sender=models.BoardGroup)
@receiver(pre_save, sender=models.Board)
def update_position_signal(sender, instance, **kwargs):
    sender.update_position(instance=instance,
                           sender=sender)