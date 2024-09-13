from decimal import Decimal
from rest_framework import serializers
from typing import Optional

from app.models import Post, PostSummary, Vote


class PostListSerializer(serializers.ModelSerializer):
    average_score = serializers.SerializerMethodField()
    score_count = serializers.SerializerMethodField()
    user_score = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = (
            "title",
            "average_score",
            "score_count",
            "user_score",
        )

    def get_average_score(self, obj: Post) -> Decimal:
        return obj.summary.average_score

    def get_score_count(self, obj: Post) -> int:
        return obj.summary.total_votes

    def get_user_score(self, obj: Post) -> Optional[int]:
        user = self.context['request'].user
        try:
            vote = Vote.objects.get(user=user, post=obj)
        except Vote.DoesNotExist:
            return None
        return vote.score
