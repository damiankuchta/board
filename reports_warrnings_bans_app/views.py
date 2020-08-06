from django.views.generic import CreateView, DetailView
from django.shortcuts import redirect
from django.contrib.admin.views.decorators import staff_member_required


from .models import Warrning, Ban


from . import models

# Create your views here.
# todo request login
class SendReport(CreateView):
    model = models.Report
    fields = ['reason']
    template_name = "reports_warrnings_bans_app/send_report.html"
    success_url = None

    model_type = None
    object = None

    def setup(self, request, *args, **kwargs):
        super(SendReport, self).setup(request, *args, **kwargs)
        self.object = self.model_type.objects.get(id=self.kwargs['object_id'])
        self.success_url = self.model_type.get_absolute_url()

    def get_context_data(self, **kwargs):
        context = super(SendReport, self).get_context_data()
        context['reported'] = self.object
        return context

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.reporting_user = self.request.user
        obj.reported_user = self.object.user
        obj.related_object = self.object
        return super(SendReport, self).form_valid(form)


class WarrningDetails(DetailView):
    model = models.Warrning
    context_object_name = "details"
    template_name = "reports_warrnings_bans_app/warrning_ban_details.html"


class BanDetails(DetailView):
    model = models.Ban
    context_object_name = "details"
    template_name = "reports_warrnings_bans_app/warrning_ban_details.html"


@staff_member_required
def add_warrning(request, user_id, object_id):
    warrning = Warrning(user_id=user_id,
                        related_object_id=object_id)
    warrning.save()
    return redirect(warrning.get_admin_url())


@staff_member_required
def add_ban(request, user_id, object_id):
    ban = Ban(user_id=user_id,
              related_object_id=object_id)
    ban.save()
    return redirect(ban.get_admin_url())