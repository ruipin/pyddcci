# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Dict, Any, Optional, List

from ..enums import *
from ..storage import T_VcpStorageIdentifier
from ..storage.storage_with_fallback import VcpStorageWithFallback

from .code import VcpCode


class VcpCodeStorage(VcpStorageWithFallback):
    # Superclass abstract methods
    def _create_value(self, code : int) -> VcpCode:
        return VcpCode(code, instance_parent=self)

    def _get_fallback_storage(self) -> 'VcpCodeStorage':
        return self.fallback

    def _wrap_fallback_storable(self, identifier : T_VcpStorageIdentifier, storable : VcpCode) -> 'FallbackVcpCode':
        from .code_fallback import FallbackVcpCode
        return FallbackVcpCode(identifier, self)


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
            code : VcpCode = self.add(value)
            code.add_name(name)
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


    # Capabilities
    def import_capabilities(self, capabilities):
        cap_codes = capabilities.get_vcp_codes()

        # Remove codes that do not exist
        for key in self.keys():
            if key not in cap_codes:
                self.remove(key)

        # Process codes
        for code_i, cap_values in cap_codes.items():
            # Add codes that are in the capabilities but not already added
            code = None
            if code_i not in self:
                code = self.add(code_i)
                code.add_name(f'Unknown Code 0x{code_i:X}')

            # Process values
            if cap_values is not None:
                if code is None:
                    code = self.get(code_i)

                    from .code_fallback import FallbackVcpCode
                    if isinstance(code, FallbackVcpCode):
                        code = code.create_wrapped_storable()

                for value_i in code.values.keys():
                    if value_i not in cap_values:
                        code.values.remove(value_i)

                #for value_i in cap_values:
                #    if value_i not in code.values:
                #        value = code.values.add(value_i)
                #        value.add_name(f'Unknown Value 0x{value_i:X}')
