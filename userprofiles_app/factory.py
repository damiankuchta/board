import factory

from . import models
from django.contrib.auth.models import Group


class GroupsFactory(factory.DjangoModelFactory):
    class Meta:
        model = Group

    name = factory.sequence(lambda x: 'test_group{id}'.format(id=x))


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.User

    username = factory.sequence(lambda x: 'test_user{user}'.format(user=x))
    password = factory.PostGenerationMethodCall("set_password", "TestPassword")
    email = factory.Faker("email")
    is_active = False

