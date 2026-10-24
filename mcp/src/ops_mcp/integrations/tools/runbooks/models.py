"""Salida de la búsqueda en runbooks."""

from __future__ import annotations

from pydantic import BaseModel


class RunbookHit(BaseModel):
    runbook: str
    title: str
    section: str
    text: str
    score: float
