from django.urls import path, include

from . import views

urlpatterns = [
    path('<slug:topic_id>/', views.Topic.as_view(), name="topic"),
    path('<slug:topic_id>/close/', views.close_topic, name="close_topic"),
    path('<slug:topic_id>/open/', views.open_topic, name="open_topic"),
    path('<slug:board_id>/new/', views.NewTopic.as_view(), name="add_new_topic"),
]
