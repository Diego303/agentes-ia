"""Dependencias que reciben las tools al registrarse.

Se construyen una vez en ``build_server`` y se pasan a cada ``register``. Los tests sustituyen
cualquiera de ellas (otro catálogo, un retriever falso, un almacén de incidentes propio).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Annotated, Any

from pydantic import Field

from ops_mcp.integrations.common.catalog import OpsCatalog
from ops_mcp.integrations.common.errors import unknown_service

if TYPE_CHECKING:
    from ops_mcp.integrations.tools.incidents.store import IncidentStore
    from opsagent_rag import Retriever


@dataclass
class ToolDeps:
    catalog: OpsCatalog
    retriever: Retriever
    incidents: IncidentStore
    auth_enabled: bool

    def service_name_type(self) -> Any:
        """Tipo del parámetro ``service``: la descripción lista los servicios válidos.

        El modelo ve en el esquema qué valores puede usar. Las tools lo usan como anotación,
        por eso sus módulos no llevan ``from __future__ import annotations``: la anotación
        tiene que evaluarse al definir la función, no después.
        """
        return Annotated[str, Field(description=f"Uno de: {', '.join(self.catalog.service_names())}")]

    async def service(self, name: str) -> dict[str, Any]:
        """Datos del servicio o un error accionable con la lista de servicios válidos."""
        data = await self.catalog.get_service(name)
        if data is None:
            raise unknown_service(name, self.catalog.service_names())
        return data
