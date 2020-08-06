from django.contrib import admin

from django.shortcuts import redirect

from . import models

# todo show is_active and expire_date, order_by
@admin.register(models.Ban)
class BanAdmin(admin.ModelAdmin):
    exclude = ['archieved']

    def response_change(self, request, obj):
        if "_setactive" in request.POST:
            obj.set_active()
            obj.save()
            return redirect(obj.get_admin_url())
        elif "_deactive" in request.POST:
            obj.de_active()
            obj.save()
            return redirect(obj.get_admin_url())
        super(BanAdmin, self).response_change(request, obj)

    def response_add(self, request, obj, post_url_continue=None):
        if "_setactive" in request.POST:
            obj.set_active()
            obj.save()
            return redirect(obj.get_admin_url())
        elif "_deactive" in request.POST:
            obj.de_active()
            obj.save()
            return redirect(obj.get_admin_url())
        super(BanAdmin, self).response_add(request, obj)

    def get_exclude(self, request, obj=None):
        excluded = super(BanAdmin, self).get_exclude(request, obj)

        #if ban is created mannually, without any report, disable all uneccesaryy fields
        if not obj:
            excluded.extend(['related_object', 'related_report',
                             "is_active", "deisplay_reason_on_related_object", "hide_related_object"])
        else:
            excluded = ['archieved']
            if not obj.related_object:
                excluded.extend(['deisplay_reason_on_related_object', 'hide_related_object', ])

        return excluded

    def get_readonly_fields(self, request, obj=None):
        readonly = super(BanAdmin, self).get_readonly_fields(request, obj)

        #if ban is active make all fieds read_only
        if obj:

            if obj.is_active:
                return  ['related_object', 'related_report', "is_active",
                         "expiry_date", 'deisplay_reason_on_related_object',
                         'hide_related_object']
            else:
                return ['related_object',  'related_report', "is_active", ]

        return readonly




@admin.register(models.Report)
class ReportAdmin(admin.ModelAdmin):
    exclude = ['archieved']
    readonly_fields = ['creation_date', 'reporting_user', 'reason', 'related_object', "reported_user",]

    def response_add(self, request, obj, post_url_continue=None):
        return None

    def response_change(self, request, obj):

        if obj:
            if "_ban" in request.POST:
                ban = models.Ban(reporting_user=obj.related_object.user,
                                 reason=obj.reason,
                                 related_report=obj,
                                 related_object=obj.related_object,
                                 reported_user=obj.reported_user)
                ban.save()
                return redirect(ban.get_admin_url())

            elif "_warrning" in request.POST:
                warrning  = models.Warrning(user=obj.reported_user,
                                            reason=obj.reason,
                                            related_report=obj,
                                            related_object = obj.related_object)
                warrning.save()
                return redirect(warrning.get_admin_url())
            elif "_archievie" in request.POST:
                obj.archieved = True
                obj.save()
                return redirect(obj.get_admin_url())
            elif "_dearchievie" in request.POST:
                obj.archieved = False
                obj.save()
                return redirect(obj.get_admin_url())

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(models.Warrning)
class WarrningAdmin(admin.ModelAdmin):
    exclude = ['']

    def get_exclude(self, request, obj=None):
        if not obj:
            self.exclude.extend(['deisplay_reason_on_related_object', 'hide_related_object',
                                 'related_object', 'related_report'])
        else:
            self.exclude = ['']

        return self.exclude

    def get_readonly_fields(self, request, obj=None):
        readonly = super(WarrningAdmin, self).get_readonly_fields(request, obj)


        if obj:
            return ['related_object',  'related_report', ]

        return readonly





