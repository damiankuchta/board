from django.db.models.signals import m2m_changed, pre_save, post_save
from django.dispatch import receiver

from . import models

"""On Group/Board group restrictions change,
it deletes from related Boards groups all Groups that are not in the Group/Board groups"""
@receiver(m2m_changed, sender=models.BoardGroup.new_posts_groups.through)
@receiver(m2m_changed, sender=models.Board.new_posts_groups.through)
@receiver(m2m_changed, sender=models.Board.visibility_groups.through)
@receiver(m2m_changed, sender=models.BoardGroup.visibility_groups.through)
@receiver(m2m_changed, sender=models.Board.new_topics_groups.through)
@receiver(m2m_changed, sender=models.BoardGroup.new_topics_groups.through)
def restriction_group_changed(instance, pk_set, action, sender, **kwargs):
    def get_sender_group_name():
        return "_".join(sender.__name__.split("_")[1:])

    senders_group_name = get_sender_group_name()

    if action == "post_remove" and getattr(instance, senders_group_name).exists():
        instance.remove_removed_restrictions_groups_from_instance_childs(pk_set=pk_set, group_name=senders_group_name)

    elif action == "pre_add" and not getattr(instance, senders_group_name).exists():
        instance.set_children_groups_to_match_its_parents(pk_set=pk_set, group_name=senders_group_name)

    elif action == "post_add":
        if instance.check_does_child_have_any_restriction_group_that_is_not_in_parent(group_name=senders_group_name):
            instance.fix_the_children_groups_to_not_have_anything_extra(group_name=senders_group_name)




@receiver(pre_save, sender=models.BoardGroup)
@receiver(pre_save, sender=models.Board)
def update_position_signal(sender, instance, **kwargs):
    sender.update_position(instance=instance,
                           sender=sender)