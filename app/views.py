from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from app.serializers import PostListSerializer
from app.models import Post
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
