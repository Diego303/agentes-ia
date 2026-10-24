"""Salida de la creación de incidentes."""

from __future__ import annotations

from pydantic import BaseModel


class Incident(BaseModel):
    id: str
    service: str
    severity: str
    summary: str
    status: str
    created_by: str
    created_at: str
