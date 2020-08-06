from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib import messages
from django.views.generic import FormView, CreateView, DetailView

from . import forms, models


"""creates account, sets active to false, and sends e-mail to given e-mail with  
activation link which will lead to activate_account"""
class SignUp(CreateView):
    template_name = "userprofiles_app/signup.html"
    form_class = forms.CustomUserCreationForm
    model = models.User
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        response = super().form_valid(form)
        form.instance.send_activation_emial(self.request)
        messages.info(self.request, "Account created, check your e-mail for activation link")
        return response


"""Activates account if token is valid"""
class ActivateYourAccount(FormView):
    def get(self, request, *args, **kwargs):
        user = models.User.objects.get(username=self.kwargs['user'])
        if user.token_generator.check_token(user, self.kwargs['token']) and not user.is_active:
            user.is_active = True
            user.save()
            messages.info(self.request, "Your account has been activated")
        else:
            messages.error(self.request, "Activation Token Invalid")
        return redirect("login")


class Profile(DetailView):
    model = models.User
    context_object_name = "profile"
    template_name = "userprofiles_app/profile.html"









