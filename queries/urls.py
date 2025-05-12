from django.urls import path
from .views import UserQueryListCreateView

urlpatterns = [
    path("", UserQueryListCreateView.as_view(), name="user_queries"),
]