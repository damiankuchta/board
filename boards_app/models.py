from enum import Enum

from django.db import models
from django.shortcuts import reverse
from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


#todo then parents visibiluit changes change its children if it doesn't matches


class BaseBoardClass(models.Model):
    class Meta:
        abstract = True
        ordering = ['position']

    class RestrictionChoices(models.IntegerChoices):
        ALL = 5
        REGISTERED = 4
        SELECTED = 3
        ADMINS = 2
        SUPERUSERS = 1
        NONE = 0

    restriction_choices = [(RestrictionChoices.ALL, 'All'),
                           (RestrictionChoices.REGISTERED, 'Registered'),
                           (RestrictionChoices.SELECTED, 'Selected Groups'),
                           (RestrictionChoices.ADMINS, 'Admins'),
                           (RestrictionChoices.SUPERUSERS, 'Superusers'),
                           (RestrictionChoices.NONE, 'None')]

    name = models.CharField(max_length=64)
    description = models.CharField(max_length=248, blank=True, null=True)
    position = models.SmallIntegerField(blank=True)
    parent = None

    visibility = models.IntegerField(choices=restriction_choices,
                                     default=RestrictionChoices.ALL,
                                     help_text="Lowest user group to be able to see Group/Board")

    visibility_groups = models.ManyToManyField(Group,
                                               related_name="%(class)s_can_view_group",
                                               blank=True,
                                               help_text="if visibility is set to 'Selected groups' set the groups")

    add_new_topics_restrictions = models.IntegerField(default=RestrictionChoices.REGISTERED,
                                                      choices=restriction_choices,
                                                      help_text="Lowest user group to be able to add new topics")

    new_topics_groups = models.ManyToManyField(Group, related_name="%(class)s_can_add_new_topics",
                                               blank=True,
                                               help_text="if new topics restricions is set "
                                                         "to 'Selected groups' set the groups")

    add_new_posts_restictions = models.IntegerField(default=RestrictionChoices.REGISTERED,
                                                    choices=restriction_choices,
                                                    help_text="Lowest user group to be able to add new posts")

    new_posts_groups = models.ManyToManyField(Group, related_name="%(class)s_can_add_new_posts",
                                              blank=True,
                                              help_text="if new post restricions is set "
                                                        "to 'Selected groups' set the groups")

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.__update_m2m_restricted_grouos_on_parent_change()
        super(BaseBoardClass, self).save(force_insert, force_update, using, update_fields)

    def can_user_add_new_topics(self, user):
        return self.__is_user_restricted(user=user, restriction_option=self.add_new_topics_restrictions)

    def can_user_view_it(self, user):
        return self.__is_user_restricted(user=user, restriction_option=self.visibility)

    def can_user_add_new_posts(self, user):
        return self.__is_user_restricted(user=user, restriction_option=self.add_new_posts_restictions)

    def __is_user_restricted(self, user, restriction_option):
        def get_resitricted_groups(restriction_option):
            if restriction_option == self.add_new_posts_restictions:
                return self.new_posts_groups
            elif restriction_option == self.add_new_topics_restrictions:
                return self.new_topics_groups
            elif restriction_option == self.visibility:
                return self.visibility_groups

        def is_user_group_in_restricted_group(user, restricted_groups):
            for group in user.groups.all():
                if group in restricted_groups:
                    return True
            return False

        if restriction_option == self.RestrictionChoices.ALL:
            return True

        elif restriction_option == self.RestrictionChoices.NONE:
            return False

        elif restriction_option == self.RestrictionChoices.REGISTERED:
            if user.is_authenticated:
                return True
            else:
                return False

        elif restriction_option == self.RestrictionChoices.SELECTED:
            restriced_groups = get_resitricted_groups(restriction_option=restriction_option)
            return is_user_group_in_restricted_group(user=user, restricted_groups=restriced_groups.all())

        elif restriction_option == self.RestrictionChoices.ADMINS:
            if user.is_staff or user.is_superuser:
                return True
            return False

        elif restriction_option == self.RestrictionChoices.SUPERUSERS:
            if user.is_superuser:
                return True
            else:
                return False

    def __update_m2m_restricted_grouos_on_parent_change(self):
        def get_new_posts_common_groups(self_object):
            return  set(self.new_posts_groups.all()).intersection(self.parent.new_posts_groups.all())

        def get_view_resitrcions_common_groups(self_object):
            return set(self.visibility_groups.all()).intersection(self.parent.visibility_groups.all())

        try:
            self_object = self.__class__.objects.get(id=self.id)
        except ObjectDoesNotExist:
            return

        if self.parent != self_object.parent:

            can_add_common =get_new_posts_common_groups(self_object)
            self.new_posts_groups.set(can_add_common)

            can_view_common = get_view_resitrcions_common_groups(self_object)
            self.visibility_groups.set(can_view_common)

    def fix_positions(self):
        children = self.child.all().order_by('position')

        for x, child in enumerate(children):
            if child.position != x+1:
                child.position = x+1
                child.save(update_fields={"position"})

    @staticmethod
    def update_position(instance, sender):
        def change_positions(new_position, old_position, siblings_list):

            if new_position == old_position:
                return
            elif new_position > old_position:
                objects_range = siblings_list.filter(position__range=(old_position, new_position)).all()
                objects_range.exclude(id=instance.id)
                objects_range.update(position=models.F('position')-1)

            else:
                objects_range = siblings_list.filter(position__range=(new_position, old_position)).all()
                objects_range.exclude(id=instance.id)
                objects_range.update(position = models.F('position')+1)

        def get_objects_siblings(pre_save_object):
                try:
                    return pre_save_object.parent.child.all()
                except AttributeError:
                    return sender.objects.all()

        def set_object_in_positions_not_exceding_minimum_or_maximum(siblings_list):
            def set_object_position_as_first():
                instance.position = 1
            def set_object_position_as_last(count_of_objects):
                if instance.id is None:
                    instance.position = count_of_objects + 1
                else:
                    instance.position = count_of_objects
            siblings_count = len(siblings_list)

            if instance.position is None:
                set_object_position_as_last(siblings_count)
            elif instance.position > siblings_count + 1:
                set_object_position_as_last(siblings_count)
            elif instance.position < 1:
                set_object_position_as_first()

        def get_pre_saved_object():
            try:
                return sender.objects.get(id=instance.id)
            except:
                return None

        def is_this_a_new_object(pre_save_object):
            return not pre_save_object == instance

        def has_parent_changed(pre_save_object):
            return instance.parent != pre_save_object.parent

        def has_position_changed(pre_save_object):
            return instance.position != pre_save_object.position

        pre_save_object = get_pre_saved_object()
        objects_siblings_list = get_objects_siblings(pre_save_object)
        set_object_in_positions_not_exceding_minimum_or_maximum(objects_siblings_list)

        if is_this_a_new_object(pre_save_object):
            change_positions(new_position=instance.position,
                             old_position=len(objects_siblings_list) + 1,
                             siblings_list=objects_siblings_list)

        elif has_parent_changed(pre_save_object):
            # change position of old siblings to fill the gap after object move
            change_positions(new_position=len(objects_siblings_list),
                             old_position=pre_save_object.position,
                             siblings_list=objects_siblings_list)

            # set position to last with new siblings
            instance.position = len(instance.parent.child.all()) + 1

        elif has_position_changed(pre_save_object):
            change_positions(new_position=instance.position,
                             old_position=pre_save_object.position,
                             siblings_list=objects_siblings_list)


    def remove_removed_restrictions_groups_from_instance_childs(self, pk_set, group_name, child_related_name="child"):
        if getattr(self, group_name).all().exists():
            try:
                child_manager = getattr(self, "{child}".format(child=child_related_name))
            except (ObjectDoesNotExist):
                return

            for child in child_manager.all():
                getattr(child, group_name).remove(*pk_set)

    def set_children_groups_to_match_its_parents(self, pk_set, group_name, child_related_name="child"):
        try:
            child_manager = getattr(self, "{child}".format(child=child_related_name))
        except (ObjectDoesNotExist):
            return

        for child in child_manager.all():
            settunio = set(getattr(child, group_name).values_list('pk', flat=True)) & set(pk_set)
            getattr(child, group_name).set(settunio)

    def fix_the_children_groups_to_not_have_anything_extra(self, group_name):
        if self.parent:
            parent_group = getattr(self.parent, group_name)
            self_group = getattr(self, group_name)
            common_groups = set(self_group.all()).intersection(set(parent_group.all()))
            if common_groups == set():
                self_group.set([])
            else:
                self_group.set(common_groups)

    def check_does_child_have_any_restriction_group_that_is_not_in_parent(self, group_name):
        if self.parent:
            parent_group = getattr(self.parent, group_name).all()
            self_group = getattr(self, group_name).all()
            return not all(item in parent_group for item in self_group)
        else:
            return False




class Board(BaseBoardClass):

    """Parent, either Board or BoardGroup"""
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    parent = GenericForeignKey('content_type', 'object_id')

    child = GenericRelation("self", null=True, on_delete=models.SET_NULL)

    def get_absolute_url(self):
        return reverse("board", kwargs={"board_id": self.id})

    # todo tes it
    def get_last_posted_topic(self):
        return self.topics.all().latest('last_post_datetime')

    # todo test it
    def get_last_posted_user(self):
        topic = self.topics.all().order_by('last_post_datetime').first()
        if topic:
            try:
                return topic.post_set.order_by("creation_datetime").first().user
            except AttributeError:
                return None
        else:
            return None

    # todo test it
    def get_post_count(self):
        count = 0
        for topic in self.topics.all():
            if topic.is_topic_visible():
                count += topic.post_set.count()
        return count

    def get_topic_count(self):
        count = 0
        for topic in self.topics.all():
            if topic.is_topic_visible():
                count += 1
        return count

    # todo test it
    def add_new_topic_url(self):
        return reverse("add_new_topic", kwargs={"board_id": self.id})

    # todo test it
    def get_all_parents(self):
        parents = [self]
        if self.parent:
            parent = self.parent
            while parent:
                parents.insert(0, parent)
                parent = parent.parent

        return parents

class BoardGroup(BaseBoardClass):
    child = GenericRelation(Board, null=True, on_delete=models.SET_NULL)

    def get_absolute_url(self):
        return reverse("board_group", kwargs={"board_group_id": self.id})


