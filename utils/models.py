from uuid import uuid4
from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(
        verbose_name="Universally Unique Identifier",
        primary_key=True, default=uuid4, editable=False,
    )
    created_at = models.DateTimeField(
        verbose_name="Created at",
        auto_now_add=True, editable=False,
    )
    updated_at = models.DateTimeField(
        verbose_name="Updated at",
        auto_now=True,
    )

    class Meta:
        abstract = True
