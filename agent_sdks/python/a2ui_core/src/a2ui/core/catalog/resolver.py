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

    def has_catalog(self, catalog_id: str) -> bool:
        """Returns whether a catalog ID is registered."""
        return catalog_id in self._catalogs

    def resolve_catalog_id(
        self,
        surface_override_id: Optional[str] = None,
        message_declared_id: Optional[str] = None,
    ) -> Optional[str]:
        """Resolves the effective catalog ID following strict 3-step fallback.

        Step 1: Surface-specific catalog override (if provided)
        Step 2: Message-declared catalog (if provided)
        Step 3: Default catalog ID
        """
        if surface_override_id:
            return surface_override_id
        if message_declared_id:
            return message_declared_id
        return self._default_catalog_id

    def resolve_catalog(
        self,
        surface_override_id: Optional[str] = None,
        message_declared_id: Optional[str] = None,
    ) -> Optional[CatalogDefinition]:
        """Resolves the CatalogDefinition using 3-step fallback.

        Returns None if the resolved catalogId is not registered in the resolver.
        """
        catalog_id = self.resolve_catalog_id(surface_override_id, message_declared_id)
        if not catalog_id:
            return None
        return self._catalogs.get(catalog_id)
