from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase

from app.models import User, Post


class BlogTestCase(TestCase):
    def setUp(self):
        super().setUp()
        self.author = User.objects.create(username="author")
        self.post = Post.objects.create(author=self.author, title="title", content="content", tags=["python"])

        self.user1 = User.objects.create(username="user1")
        self.user2 = User.objects.create(username="user2")
        self.user3 = User.objects.create(username="user3")

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
