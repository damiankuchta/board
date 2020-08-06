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

    ALL = 5
    REGISTERED = 4
    SELECTED = 3
    ADMINS = 2
    SUPERUSERS = 1
    NONE = 0

    choices = [ (ALL, 'All'),
                (REGISTERED, 'Registered'),
                (SELECTED, 'Selected Groups'),
                (ADMINS, 'Admins'),
                (SUPERUSERS, 'Superusers'),
                (NONE, 'None'),]

    name = models.CharField(max_length=64)
    description = models.CharField(max_length=248, blank=True, null=True)
    position = models.SmallIntegerField(blank=True)
    parent = None


    # ---------------------------------------------------------------------------------------------------------

    visibility = models.IntegerField(choices=choices, default=ALL,
                                  help_text="Lowest user group to be able to see Group/Board")

    visibility_groups = models.ManyToManyField(Group,  related_name="%(class)s_can_view_group", blank=True,
                                               help_text="if visibility is set to 'Selected groups' set the groups")

    # ---------------------------------------------------------------------------------------------------------

    add_new_topics_restrictions = models.IntegerField(default=REGISTERED,  choices=choices,
                                                   help_text="Lowest user group to be able to add new topics")

    new_topics_groups = models.ManyToManyField(Group, related_name="%(class)s_can_add_new_topics", blank=True,
                                               help_text="if new topics restricions is set "
                                                         "to 'Selected groups' set the groups")

    # ---------------------------------------------------------------------------------------------------------

    add_new_posts_restictions = models.IntegerField(default=REGISTERED, choices=choices,
                                                 help_text="Lowest user group to be able to add new posts")

    new_posts_groups = models.ManyToManyField(Group, related_name="%(class)s_can_add_new_posts", blank=True,
                                              help_text="if new post restricions is set "
                                                        "to 'Selected groups' set the groups")

    # ---------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.__update_m2m_restricted_grouos_on_parent_change()
        super(BaseBoardClass, self).save(force_insert, force_update, using, update_fields)

    #used in template tag
    #todo test it!!
    def is_user_restricted(self, user, act):

        action = None
        group = None

        if act == "post":
            action = self.add_new_posts_restictions
            group = self.new_posts_groups
        elif act == "topic":
            action = self.add_new_topics_restrictions
            group = self.new_topics_groups
        elif act == "visibility":
            action = self.visibility
            group = self.visibility_groups
        else:
            return False

        # all
        if action == self.ALL:
            return True

        # none
        elif action == self.NONE:
            return False

        # registered
        elif action == self.REGISTERED:
            if user.is_authenticated:
                return True
            else:
                return False

        # selected
        elif action == self.SELECTED:
            if user.is_staff or user.is_superuser:
                return True
            for g in user.groups.all():
                if g in group:
                    return True
            return False

        # admins
        elif action == self.ADMINS:
            if user.is_staff or user.is_superuser:
                return True
            return False

        #superuser
        elif action == self.SUPERUSERS:
            if user.is_superuser:
                return True
            return False

    """ 
        USED IN SIGNAL PRE_SAVE
        on saves checks if position/parent was changed if it was it updates positions of other
        siblings to make sure all positions are in proper sequence
    """
    @staticmethod
    def update_position(instance, sender):
        def change_positions(new_position, old_position, objects_set):

            if new_position == old_position:
                return
            elif new_position > old_position:
                objects_range = objects_set.filter(position__range=(old_position, new_position)).all()
                objects_range.exclude(id=instance.id)
                objects_range.update(position=models.F('position')-1)

            else:
                objects_range = objects_set.filter(position__range=(new_position, old_position)).all()
                objects_range.exclude(id=instance.id)
                objects_range.update(position = models.F('position')+1)

        def get_objects_with_the_same_parent(parent):
            if parent:
                objects_with_same_parent = sender.objects.filter(object_id=parent.id)
            else:
                objects_with_same_parent = sender.objects.all()
            return objects_with_same_parent

        #takes either 1 or 0
        def set_position(is_object_added_to_model: int):
            if instance.position is None or \
                    instance.position > objects_with_same_parent.count()+is_object_added_to_model:
                instance.position = objects_with_same_parent.count() + is_object_added_to_model
            elif instance.position < 1 or objects_with_same_parent.count() == 0:
                instance.position = 1

        try:
            old_object = sender.objects.get(id=instance.id)
        except ObjectDoesNotExist:
            objects_with_same_parent = get_objects_with_the_same_parent(instance.parent)
            set_position(1)
            change_positions(instance.position,
                             objects_with_same_parent.count() + 1,
                             objects_with_same_parent)
            return
        else:
            objects_with_same_parent = get_objects_with_the_same_parent(old_object.parent)
            set_position(0)

            #Imitate moving to last position
            if instance.parent != old_object.parent:
                change_positions(new_position=objects_with_same_parent.count()+1,
                                 old_position=old_object.position,
                                 objects_set=objects_with_same_parent)
                instance.position = instance.parent.child.count()+1

            elif instance.position != old_object.position:
                change_positions(new_position=instance.position,
                                 old_position=old_object.position,
                                 objects_set=objects_with_same_parent)


    """
        on restriction group change, check what was changed and match the restrictiong groups
        of childs to the restriction group of parents
    """
    def __update_m2m_restricted_grouos_on_parent_change(self):

        try:
            self_object = self.__class__.objects.get(id=self.id)
        except ObjectDoesNotExist:
            return

        if self.parent != self_object.parent:
            can_add_common = set(self.new_posts_groups.all())\
                .intersection(self.parent.new_posts_groups.all())

            can_view_common = set(self.visibility_groups.all())\
                .intersection(self.parent.visibility_groups.all())

            self.new_posts_groups.set(can_add_common)
            self.visibility_groups.set(can_view_common)


    """to be used in signal, updates all the child restrictions groups of objects childs"""
    @staticmethod
    def update_restrictions_groups(pk_set, action, group, instance, child_related_name="child"):

        if action == "post_remove":
            if getattr(instance, group).all().exists():

                try:
                    child_manager = getattr(instance, "{child}".format(child=child_related_name))
                except (ObjectDoesNotExist):
                    return

                for child in child_manager.all():
                    getattr(child, group).remove(*pk_set)

        elif action == "pre_add":
            if not getattr(instance, group).all().exists():

                try:
                    child_manager = getattr(instance, "{child}".format(child=child_related_name))
                except (ObjectDoesNotExist):
                    return


                for child in child_manager.all():
                    settunio = set(getattr(child, group).values_list('pk', flat=True)) & set(pk_set)
                    getattr(child, group).set(settunio)

    def can_user_add_new_topics(self, user):
        return self.is_user_restricted(user=user, act="topic")

    def can_user_view_it(self, user):
        return self.is_user_restricted(user=user, act="visibility")

    def can_user_add_new_posts(self, user):
        return self.is_user_restricted(user=user, act="post")


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


