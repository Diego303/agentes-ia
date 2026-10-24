"""Incidentes: almacén (``store``), modelos de salida (``models``) y la tool (``tool``)."""

from ops_mcp.integrations.tools.incidents.store import IncidentStore
from ops_mcp.integrations.tools.incidents.tool import NAME, register

__all__ = ["NAME", "IncidentStore", "register"]
