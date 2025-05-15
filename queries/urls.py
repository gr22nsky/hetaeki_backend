from django.urls import path
from .views import QueryAnswerView, HotTopicView

urlpatterns = [
    path("", QueryAnswerView.as_view(), name="user_queries"),
    path("hottopics/", HotTopicView.as_view(), name="hot_topic"),
]