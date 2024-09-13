from uuid import uuid4
from django.db import models
from drf_spectacular.utils import (
    extend_schema,
    Serializer,
    OpenApiExample,
    OpenApiCallback,
    OpenApiParameter,
    Promise,
)
from typing import Optional, Sequence, Union, Type, Any


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


def schema_decorator(*args, **kwargs):
    def decorator(decorated_class):
        decorated_class = extend_schema(*args, **kwargs)(decorated_class)
        return decorated_class
    return decorator


class SchemaDecorator(type):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        kwargs = {}
        for attr, value in attrs.items():
            if attr.startswith("schema_"):
                kwargs[attr.replace("schema_", "")] = value

        decorated_class = schema_decorator(**kwargs)(cls)
        globals()[name] = decorated_class


class ExtendedSchema(metaclass=SchemaDecorator):
    schema_operation_id: Optional[str]
    schema_parameters: Optional[Sequence[Union[OpenApiParameter, Union[Serializer, Type[Serializer]]]]]
    schema_request: Any
    schema_response: Any
    schema_auth: Optional[Sequence[str]]
    schema_description: Optional[Union[str, Promise]]
    schema_summary: Optional[Union[str, Promise]]
    schema_deprecated: Optional[bool]
    schema_tags: Optional[Sequence[str]]
    schema_filters: Optional[bool]
    schema_exclude: Optional[bool]
    schema_operation: Optional[dict[str, Any]]
    schema_methods: Optional[Sequence[str]]
    schema_versions: Optional[Sequence[str]]
    schema_examples: Optional[Sequence[OpenApiExample]]
    schema_extensions: Optional[dict[str, Any]]
    schema_callbacks: Optional[Sequence[OpenApiCallback]]
    schema_external_docs: Optional[Union[dict[str, str], str]]

    http_method_names = [
        "get",
        "post",
        "put",
        "patch",
        "delete",
        "head",
        "options",
        "trace",
    ]
