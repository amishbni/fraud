from django.urls import re_path

from app.views import PostListView

app_name = "app"
urlpatterns = [
    re_path(r"blog/posts/?$", PostListView.as_view(), name="post-list"),
]
