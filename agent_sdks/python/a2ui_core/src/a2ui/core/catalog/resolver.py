"""Strict 3-step Catalog Resolver for A2UI v1.0.

Implements the 3-step catalog resolution fallback algorithm:
1. Surface-specific catalog override
2. Message-declared catalog
3. Default catalog
"""

from typing import Dict, Optional
from a2ui.core.catalog.catalog_definition import CatalogDefinition


class CatalogResolver:
    """Resolves effective catalog definitions using strict 3-step fallback."""

    def __init__(
        self,
        catalogs: Optional[Dict[str, CatalogDefinition]] = None,
        default_catalog_id: Optional[str] = None,
    ) -> None:
        """Initializes resolver with optional catalogs dictionary and default ID."""
        self._catalogs: Dict[str, CatalogDefinition] = (
            catalogs.copy() if catalogs else {}
        )
        self._default_catalog_id: Optional[str] = default_catalog_id

    def register_catalog(self, catalog: CatalogDefinition) -> None:
        """Registers a catalog definition."""
        self._catalogs[catalog.catalog_id] = catalog

    def resolve_catalog_id(
        self,
        surface_override_id: Optional[str] = None,
        message_declared_id: Optional[str] = None,
    ) -> Optional[str]:
        """Resolves the effective catalog ID following strict 3-step fallback.

        Step 1: Surface-specific catalog override
        Step 2: Message-declared catalog
        Step 3: Default catalog ID
        """
        if surface_override_id and surface_override_id in self._catalogs:
            return surface_override_id
        if message_declared_id and message_declared_id in self._catalogs:
            return message_declared_id
        if self._default_catalog_id and self._default_catalog_id in self._catalogs:
            return self._default_catalog_id

        # Return first non-None match even if not in catalogs map
        return surface_override_id or message_declared_id or self._default_catalog_id

    def resolve_catalog(
        self,
        surface_override_id: Optional[str] = None,
        message_declared_id: Optional[str] = None,
    ) -> Optional[CatalogDefinition]:
        """Resolves the CatalogDefinition using 3-step fallback."""
        catalog_id = self.resolve_catalog_id(surface_override_id, message_declared_id)
        if not catalog_id:
            return None
        return self._catalogs.get(catalog_id)
