"""Búsqueda en runbooks: índice (``index``), modelos de salida (``models``) y la tool (``tool``)."""

from ops_mcp.integrations.tools.runbooks.index import RUNBOOKS_DIR, build_retriever
from ops_mcp.integrations.tools.runbooks.tool import NAME, register

__all__ = ["NAME", "RUNBOOKS_DIR", "build_retriever", "register"]
