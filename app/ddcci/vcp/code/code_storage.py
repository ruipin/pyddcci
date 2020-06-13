# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Dict, Any, Optional, List, Hashable

from ..enums import *
from ..storage.storage_with_fallback import VcpStorageWithFallback

from .code import VcpCode


class VcpCodeStorage(VcpStorageWithFallback):
    # Superclass abstract methods
    def _is_storable_value(self, obj : Any) -> bool:
        return isinstance(obj, VcpCode)

    def _create_value(self, code : int) -> VcpCode:
        return VcpCode(code, instance_parent=self)

    def _get_fallback(self) -> 'VcpCodeStorage':
        return self._fallback if hasattr(self, '_fallback') else None

    def _set_fallback(self, new_fallback: 'VcpCodeStorage') -> None:
        self._fallback = new_fallback

    def _get_fallback_storage(self) -> 'VcpCodeStorage':
        return self.fallback

    def _wrap_fallback_storable(self, name : Hashable, storable : VcpCode) -> 'FallbackVcpCode':
        from .code_fallback import FallbackVcpCode
        return FallbackVcpCode(name, self)


    # Add from dictionary
    def _add_dictionary_key(self, value: int, details: Dict[str, Any], category: Optional[str]):
        name = details["name"]

        try:
            type = details.get('type', None)
            if type is not None:
                type = VcpControlType(type)

            description = details.get('description', None)

            aliases : Optional[str, List[str]] = details.get('aliases', None)
            if aliases is not None and not isinstance(aliases, list):
                aliases = [aliases]

            sub_values = details.get('values', None)

            verify = details.get('verify', False)

            # Add code
            code = self.add(value)
            self[name] = code
            code.type = type
            code.description = description
            code.category = category
            code.verify = verify

            if aliases is not None:
                for alias in aliases:
                    self.set(alias, value)

            if sub_values is not None:
                for value, names in sub_values.items():
                    if isinstance(names, str):
                        code.add_value(names, value)
                    else:
                        for nm in names:
                            code.add_value(nm, value)

        except Exception as e:
            self.log.exception(f"Failed to add dictionary key '{name}'")
            raise


    def add_dictionary(self, d):
        for k, v in d.items():
            # String keys are categories
            if isinstance(k, str):
                category = k
                for k2, v2 in v.items():
                    self._add_dictionary_key(k2, v2, category)
                continue

            # Otherwise, add directly
            self._add_dictionary_key(k, v, None)