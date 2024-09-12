from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction

from utils.models import BaseModel


class User(BaseModel):
    username = models.CharField(
        verbose_name="Username",
        max_length=255, unique=True,
    )

    def __str__(self):
        return self.username

    def vote(self, post: "Post", score: int) -> "Vote":
        vote, _ = Vote.objects.update_or_create(
            user=self,
            post=post,
            defaults={"score": score},
        )
        return vote


class Post(BaseModel):
    author = models.ForeignKey(
        User, verbose_name="Author",
        on_delete=models.CASCADE, related_name="posts",
    )
    title = models.CharField(
        verbose_name="Title",
        max_length=255,
    )
    content = models.TextField(
        verbose_name="Content",
    )
    tags = ArrayField(
        models.CharField(max_length=50), verbose_name="Tags",
    )

    def __str__(self):
        return self.title


class Vote(BaseModel):
    user = models.ForeignKey(
        User, verbose_name="Vote",
        on_delete=models.CASCADE, related_name="votes",
    )
    post = models.ForeignKey(
        Post, verbose_name="Post",
        on_delete=models.CASCADE, related_name="votes",
    )
    score = models.PositiveSmallIntegerField(
        verbose_name="Vote Score",
        validators=[MinValueValidator(0), MaxValueValidator(5)],
    )
    reversed = models.BooleanField(
        verbose_name="Reversed",
        help_text="The vote is reversed (excluded from count and average) if it's detected as fraudulent",
        default=False,
    )

    def __str__(self):
        return f"{self.user} on {self.post}: {self.score}"

    def save(self, *args, **kwargs):
        self.full_clean()

        if self._state.adding:
            super().save(*args, **kwargs)
            PostSummary.update(post=self.post, new_score=self.score)
        else:
            old_score: int = Vote.objects.get(pk=self.pk).score
            super().save(*args, **kwargs)
            PostSummary.update(post=self.post, new_score=self.score, old_score=old_score)

    def reverse(self):
        PostSummary.update(post=self.post, new_score=self.score, reverse=True)
        self.reversed = True
        self.save(update_fields=["reversed"])

    class Meta:
        unique_together = ("user", "post",)


class PostSummary(BaseModel):
    post = models.OneToOneField(Post, verbose_name="Post", on_delete=models.CASCADE, related_name="summary")
    total_votes = models.PositiveBigIntegerField(
        verbose_name="Total Votes",
        default=0,
    )
    average_score = models.DecimalField(
        verbose_name="Average Score",
        max_digits=4, decimal_places=3, default=0.0,
    )

    def __str__(self):
        return f"Post: {self.post}, Total Votes: {self.total_votes}, Average Score: {self.average_score}"

    @classmethod
    @transaction.atomic
    def update(
            cls,
            post: Post,
            new_score: int,
            old_score: int = None,
            reverse: bool = False,
            *args,
            **kwargs,
    ) -> "PostSummary":
        if old_score is not None and reverse:
            raise Exception("Can't update and reverse vote at the same time")

        post_summary, _ = cls.objects.select_for_update().get_or_create(post=post)
        new_votes: int = 1

        if reverse:
            new_votes *= -1
            new_score *= -1

        if old_score is None:
            post_summary.average_score = (
                (post_summary.average_score * post_summary.total_votes + new_score) /
                (post_summary.total_votes + new_votes)
            )
            post_summary.total_votes += new_votes
        else:
            post_summary.average_score = (
                (post_summary.average_score * post_summary.total_votes - old_score + new_score) /
                post_summary.total_votes
            )

        post_summary.save(update_fields=["total_votes", "average_score"])
        return post_summary
