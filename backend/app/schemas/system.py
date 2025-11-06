"""System level schemas."""

from __future__ import annotations

from typing import Dict

from pydantic import BaseModel


class HealthComponent(BaseModel):
    status: str
    detail: str | None = None


class HealthResponse(BaseModel):
    status: str
    components: Dict[str, HealthComponent]


class SystemInfoResponse(BaseModel):
    project_name: str
    version: str
    description: str
    features: Dict[str, bool]


__all__ = ["HealthComponent", "HealthResponse", "SystemInfoResponse"]

