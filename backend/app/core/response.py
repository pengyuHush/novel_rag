"""Custom response classes for API."""

from __future__ import annotations

from typing import Any

from fastapi.responses import JSONResponse
from pydantic import BaseModel


class CamelCaseJSONResponse(JSONResponse):
    """JSON response that uses camelCase field names (Pydantic aliases)."""

    def render(self, content: Any) -> bytes:
        """Render content as JSON, using Pydantic aliases if applicable."""
        if isinstance(content, BaseModel):
            # Use by_alias=True to convert to camelCase
            content = content.model_dump(mode="json", by_alias=True)
        elif isinstance(content, dict):
            # Check if any values are Pydantic models
            content = {
                k: v.model_dump(mode="json", by_alias=True) if isinstance(v, BaseModel) else v
                for k, v in content.items()
            }
        return super().render(content)


__all__ = ["CamelCaseJSONResponse"]

