from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView, PasswordResetConfirmView, PasswordResetView
from django.urls import reverse_lazy

from . import views

urlpatterns = [

    path('login/', LoginView.as_view(
             template_name="userprofiles_app/login.html"),
         name="login"),

    path('logout/', LogoutView.as_view(),
         name="logout"),

    path('signup/', views.SignUp.as_view(),
         name="signup"),

    path('confirm_emial/', PasswordResetView.as_view(
        template_name="userprofiles_app/forgotten_password.html",
        email_template_name="userprofiles_app/emials/email_reset_password.html",
        html_email_template_name = "userprofiles_app/emials/email_reset_password.html",
        success_url = reverse_lazy("login")
    ),
         name="get_reset_token"),

    path('reset_password/<uidb64>/<token>', PasswordResetConfirmView.as_view(
             template_name="userprofiles_app/chnage_password.html")
         ,
         name="reset_password"),

    path('activate_account/<str:user>/<str:token>/', views.ActivateYourAccount.as_view(), name="activate_account"),

    path('profile/<int:pk>', views.Profile.as_view(), name="profile"),
]