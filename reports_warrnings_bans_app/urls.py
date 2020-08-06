from django.urls import path, include

from . import models
from topics_app.models import Post

from . import views

urlpatterns = [
    path('post/<int:object_id>/', views.SendReport.as_view(model_type=Post), name="report_post"),
    path('pm/<int:object_id>/', views.SendReport.as_view(model_type=Post), name="report_pm"),


    path('warrning/<int:user_id>/<int:object_id>/', views.add_warrning, name="add_warrning"),
    path('ban/<int:user_id>/<int:object_id>/', views.add_ban, name="add_ban"),
    path('warrning/<int:pk>/', views.WarrningDetails.as_view(), name="warrning_detail"),
    path('ban/<int:pk>/', views.BanDetails.as_view(), name="ban_detail"),
]
