from django.urls import re_path

from app.views import PostListView, CastVoteView

app_name = "app"
urlpatterns = [
    re_path(
        r"blog/posts/?$",
        PostListView.as_view(),
        name="post-list",
    ),
    re_path(
        r"blog/posts/(?P<post>[0-9a-fA-F-]{36})/vote/(?P<score>[0-9])/?$",
        CastVoteView.as_view(),
        name="cast-vote",
    )
]
