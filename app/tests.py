from datetime import timedelta
from decimal import Decimal
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase
from django.utils import timezone

from app.models import User, Post, Vote
from app.tasks import fraud_detection


class BlogTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.author = User.objects.create(username="author")
        self.post = Post.objects.create(author=self.author, title="title", content="content", tags=["python"])

        self.user1 = User.objects.create(username="user1")
        self.user2 = User.objects.create(username="user2")
        self.user3 = User.objects.create(username="user3")
        self.user4 = User.objects.create(username="user4")
        self.user5 = User.objects.create(username="user5")
        self.user6 = User.objects.create(username="user6")
        self.user7 = User.objects.create(username="user7")
        self.user8 = User.objects.create(username="user8")
        self.user9 = User.objects.create(username="user9")
        self.user10 = User.objects.create(username="user10")
        self.user11 = User.objects.create(username="user11")

    def test_average_score(self):
        self.user1.vote(post=self.post, score=2)
        self.post.refresh_from_db()

        self.assertEqual(self.post.summary.total_votes, 1)
        self.assertEqual(self.post.summary.average_score, 2)

        self.user2.vote(post=self.post, score=3)
        self.post.refresh_from_db()

        self.assertEqual(self.post.summary.total_votes, 2)
        self.assertEqual(self.post.summary.average_score, 2.5)

    def test_update_score(self):
        self.user1.vote(post=self.post, score=1)
        self.user2.vote(post=self.post, score=2)
        self.user3.vote(post=self.post, score=3)
        self.post.refresh_from_db()

        self.assertEqual(self.post.summary.total_votes, 3)
        self.assertEqual(self.post.summary.average_score, 2)

        self.user1.vote(post=self.post, score=4)
        self.post.refresh_from_db()

        self.assertEqual(self.post.summary.total_votes, 3)
        self.assertEqual(self.post.summary.average_score, 3)

    def test_atomicity(self):
        self.user1.vote(post=self.post, score=2)

        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.user2.vote(post=self.post, score=3)
                raise IntegrityError("Unexpected error")

        self.post.refresh_from_db()

        self.assertEqual(self.post.summary.total_votes, 1)
        self.assertEqual(self.post.summary.average_score, 2)

    def test_out_of_bound_score(self):
        self.user1.vote(post=self.post, score=3)

        with self.assertRaises(ValidationError):
            self.user2.vote(post=self.post, score=6)

        with self.assertRaises(ValidationError):
            self.user2.vote(post=self.post, score=-1)

        self.assertEqual(self.post.summary.total_votes, 1)
        self.assertEqual(self.post.summary.average_score, 3)

    def test_reverse_vote(self):
        user1_vote = self.user1.vote(post=self.post, score=4)
        user2_vote = self.user2.vote(post=self.post, score=5)
        self.post.refresh_from_db()

        self.assertFalse(user1_vote.reversed)
        self.assertFalse(user2_vote.reversed)
        self.assertEqual(self.post.summary.total_votes, 2)
        self.assertEqual(self.post.summary.average_score, 4.5)

        user2_vote.reverse()
        self.post.refresh_from_db()

        self.assertFalse(user1_vote.reversed)
        self.assertTrue(user2_vote.reversed)
        self.assertEqual(self.post.summary.total_votes, 1)
        self.assertEqual(self.post.summary.average_score, 4)

    def test_z_score(self):
        now = timezone.now()
        Vote.objects.create(created_at=(now - timedelta(hours=2)), user=self.user1, post=self.post, score=2)
        Vote.objects.create(created_at=(now - timedelta(hours=3)), user=self.user2, post=self.post, score=3)
        Vote.objects.create(created_at=(now - timedelta(hours=4)), user=self.user3, post=self.post, score=4)
        Vote.objects.create(created_at=(now - timedelta(hours=5)), user=self.user4, post=self.post, score=3)
        Vote.objects.create(created_at=(now - timedelta(hours=6)), user=self.user5, post=self.post, score=4)
        Vote.objects.create(created_at=(now - timedelta(hours=7)), user=self.user6, post=self.post, score=2)
        Vote.objects.create(created_at=(now - timedelta(hours=8)), user=self.user7, post=self.post, score=3)
        Vote.objects.create(created_at=(now - timedelta(hours=9)), user=self.user8, post=self.post, score=5)
        Vote.objects.create(created_at=(now - timedelta(hours=10)), user=self.user9, post=self.post, score=2)

        fraudulent_vote = (
            Vote.objects.create(created_at=(now - timedelta(minutes=10)), user=self.user10, post=self.post, score=0)
        )
        real_vote = (
            Vote.objects.create(created_at=(now - timedelta(minutes=15)), user=self.user11, post=self.post, score=4)
        )
        real_votes_24_hours_ago = (
            Vote.objects
            .filter(
                reversed=False,
                created_at__gte=(now - timedelta(hours=24))
            )
        )

        self.assertGreaterEqual(
            abs(fraudulent_vote.z_score(recent_votes=real_votes_24_hours_ago)),
            settings.Z_SCORE_THRESHOLD,
        )
        self.assertLess(
            abs(real_vote.z_score(recent_votes=real_votes_24_hours_ago)),
            settings.Z_SCORE_THRESHOLD,
        )

    def test_fraud_detection(self):
        now = timezone.now()
        Vote.objects.create(created_at=(now - timedelta(hours=2)), user=self.user1, post=self.post, score=3)
        Vote.objects.create(created_at=(now - timedelta(hours=3)), user=self.user2, post=self.post, score=2)
        Vote.objects.create(created_at=(now - timedelta(hours=4)), user=self.user3, post=self.post, score=3)
        Vote.objects.create(created_at=(now - timedelta(hours=5)), user=self.user4, post=self.post, score=5)
        Vote.objects.create(created_at=(now - timedelta(hours=6)), user=self.user5, post=self.post, score=2)
        Vote.objects.create(created_at=(now - timedelta(hours=7)), user=self.user6, post=self.post, score=3)
        Vote.objects.create(created_at=(now - timedelta(hours=8)), user=self.user7, post=self.post, score=4)
        Vote.objects.create(created_at=(now - timedelta(hours=9)), user=self.user8, post=self.post, score=2)
        Vote.objects.create(created_at=(now - timedelta(hours=10)), user=self.user9, post=self.post, score=3)

        self.post.refresh_from_db()

        self.assertEqual(self.post.summary.total_votes, 9)
        self.assertEqual(self.post.summary.average_score, 3)

        fraudulent_vote = (
            Vote.objects.create(created_at=(now - timedelta(minutes=15)), user=self.user10, post=self.post, score=0)
        )
        real_vote = (
            Vote.objects.create(created_at=(now - timedelta(minutes=10)), user=self.user11, post=self.post, score=4)
        )

        fraud_detection()

        fraudulent_vote.refresh_from_db()
        real_vote.refresh_from_db()
        self.post.refresh_from_db()

        self.assertTrue(fraudulent_vote.reversed)
        self.assertFalse(real_vote.reversed)

        self.assertEqual(self.post.summary.total_votes, 10)
        self.assertEqual(self.post.summary.average_score, Decimal("3.1"))
