from rest_framework import status
from rest_framework.generics import ListAPIView, GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from app.serializers import PostListSerializer, CastVoteSerializer
from app.models import Post, Vote
from utils.constants import Namespace
from utils.models import ExtendedSchema


class PostListView(ExtendedSchema, ListAPIView):
    schema_tags = [Namespace.POST.value]
    serializer_class = PostListSerializer
    permission_classes = [IsAuthenticated]
    queryset = Post.objects.all()
    http_method_names = ["get"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class CastVoteView(ExtendedSchema, GenericAPIView):
    schema_tags = [Namespace.USER.value]
    serializer_class = CastVoteSerializer
    permission_classes = [IsAuthenticated]
    queryset = Vote.objects.all()
    http_method_names = ["post"]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def post(self, request, *args, **kwargs):
        user = self.request.user
        post = Post.objects.get(pk=kwargs.get("post"))
        score = kwargs.get("score")

        vote = user.vote(post=post, score=score)

        serializer = self.get_serializer(instance=vote)
        return Response(serializer.data, status=status.HTTP_200_OK)
