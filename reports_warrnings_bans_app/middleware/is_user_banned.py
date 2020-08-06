from django.utils import timezone

from django.shortcuts import HttpResponse

from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth import logout


class IsUserBanned(MiddlewareMixin):
    def process_request(self, request):
        user = request.user
        if user.is_authenticated:
            ban_date = user.reports_warrnings_bans_app_ban.all().latest("expiry_date").expiry_date
            if ban_date and ban_date > timezone.now() and not (user.is_superuser or user.is_staff):
                logout(request)

                # todo http response
                return HttpResponse("Banned")
        return None
