"""Custom APIRouter with camelCase response support."""

from __future__ import annotations

from typing import Any, Callable, Sequence

from fastapi import APIRouter as FastAPIRouter
from fastapi.types import DecoratedCallable


class APIRouter(FastAPIRouter):
    """Custom APIRouter that uses camelCase (by_alias=True) for all responses."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize with default response_model_by_alias=True."""
        # Don't set it here as it's not a constructor parameter
        super().__init__(*args, **kwargs)

    def add_api_route(
        self,
        path: str,
        endpoint: Callable[..., Any],
        *,
        response_model_by_alias: bool = True,
        **kwargs: Any,
    ) -> None:
        """Override add_api_route to default response_model_by_alias to True."""
        super().add_api_route(
            path, endpoint, response_model_by_alias=response_model_by_alias, **kwargs
        )

    def get(
        self, path: str, *, response_model_by_alias: bool = True, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        """GET method with camelCase aliases."""
        return super().get(path, response_model_by_alias=response_model_by_alias, **kwargs)

    def post(
        self, path: str, *, response_model_by_alias: bool = True, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        """POST method with camelCase aliases."""
        return super().post(path, response_model_by_alias=response_model_by_alias, **kwargs)

    def put(
        self, path: str, *, response_model_by_alias: bool = True, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        """PUT method with camelCase aliases."""
        return super().put(path, response_model_by_alias=response_model_by_alias, **kwargs)

    def delete(
        self, path: str, *, response_model_by_alias: bool = True, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        """DELETE method with camelCase aliases."""
        return super().delete(path, response_model_by_alias=response_model_by_alias, **kwargs)

    def patch(
        self, path: str, *, response_model_by_alias: bool = True, **kwargs: Any
    ) -> Callable[[DecoratedCallable], DecoratedCallable]:
        """PATCH method with camelCase aliases."""
        return super().patch(path, response_model_by_alias=response_model_by_alias, **kwargs)


__all__ = ["APIRouter"]

