from django.db import models
from django.shortcuts import reverse

from userprofiles_app.models import User
from topics_app.models import Post



"""base class for all models"""
class BaseClass(models.Model):
    class Meta:
        abstract = True

    related_object = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, related_name="%(app_label)s_%(class)s")  # POST/PM?
    creation_date = models.DateTimeField(auto_now_add=True)
    reason = models.TextField()

# ----------------------------------------------------------------------------------------------------------------------


class Report(BaseClass):
    reporting_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="user_reports")
    reported_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="reports_on_user")
    archieved = models.BooleanField(default=False)

    def get_admin_url(self):
        return '/admin/reports_warrnings_bans_app/report/{}/change/'.format(self.pk)

# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------
# ----------------------------------------------------------------------------------------------------------------------

"""Base class for warrning and ban class"""
class BanWarrningBaseClass(BaseClass):
    class Meta:
        abstract = True

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="%(app_label)s_%(class)s")
    deisplay_reason_on_related_object = models.BooleanField(default=True)
    hide_related_object = models.BooleanField(default=True)
    related_object = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, related_name="%(app_label)s_%(class)s")  # POST/PM?
    related_report = models.ForeignKey(Report, on_delete=models.SET_NULL, null=True, related_name="%(app_label)s_%(class)s")

    def get_absolute_url(self):
        return reverse("{}_detail".format((self.__class__.__name__).lower()), kwargs={"pk": self.pk})

    def get_self_class_name(self):
        return self.__class__.__name__

# ----------------------------------------------------------------------------------------------------------------------


class Warrning(BanWarrningBaseClass):
    def get_admin_url(self):
        return '/admin/reports_warrnings_bans_app/warrning/{}/change/'.format(self.pk)


class Ban(BanWarrningBaseClass):
    expiry_date = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=False)

    def get_admin_url(self):
        return '/admin/reports_warrnings_bans_app/ban/{}/change/'.format(self.pk)


    def set_active(self):
        if self.related_report:
            self.related_report.archieved = True
            self.related_report.save()
        self.is_active = True

    def de_active(self):
        self.is_active = False

    def is_ban_active(self):
        return self.is_active

    def __str__(self):
        return " {} ".format(self.user)

    def get_expiry_date(self):
        return self.expiry_date







