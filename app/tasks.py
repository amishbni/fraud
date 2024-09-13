from celery import shared_task
from datetime import timedelta
from django.conf import settings
from django.utils import timezone

from app.models import Vote


@shared_task
def fraud_detection():
    now = timezone.now()
    last_30_minutes = now - timedelta(minutes=30)
    last_24_hours = now - timedelta(hours=24)

    votes_30_minutes_ago = (
        Vote.objects
        .filter(
            created_at__gte=last_30_minutes,
        )
    )

    real_votes_24_hours_ago = (
        Vote.objects
        .filter(
            reversed=False,
            created_at__gte=last_24_hours,
        )
    )

    for vote in votes_30_minutes_ago:
        if abs(vote.z_score(recent_votes=real_votes_24_hours_ago)) >= settings.Z_SCORE_THRESHOLD:
            vote.reverse()
