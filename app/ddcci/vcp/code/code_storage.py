# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Dict, Any, Optional, List, Union

from ..enums import *
from ..storage.storage import VcpStorage

from .code import VcpCode


class VcpCodeStorage(VcpStorage[VcpCode]):
    """
    Storage for VcpCode objects, providing methods to add, retrieve, and manage VCP codes and their metadata.
    Handles loading from dictionaries, capability parsing, and serialization.
    """
    def _create_value(self, key : int) -> VcpCode:
        """
        Create a new VcpCode instance for the given code.

        Args:
            code: The VCP code integer value.

        Returns:
            VcpCode: The created VcpCode instance.
        """
        return VcpCode(key, instance_parent=self)


    def _add_dictionary_key(self, value: int, details: Dict[str, Any], category: Optional[str]):
        """
        Add a VCP code and its details from a dictionary entry.

        Args:
            value: The VCP code integer value.
            details: Dictionary of code details (name, type, aliases, etc.).
            category: Optional category name.
        """
        name = details["name"]

        try:
            type = details.get('type', None)
            if type is not None:
                type = VcpControlType(type)

            description = details.get('description', None)

            aliases : str | List[str] | None = details.get('aliases', None)
            if aliases is not None and not isinstance(aliases, list):
                aliases = [aliases]

            sub_values = details.get('values', None)

            # Add code
            code : VcpCode = self.add(value)
            code.add_name(name)
            code.type = type
            code.description = description
            code.category = category

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
        """
        Add multiple VCP codes from a dictionary.

        Args:
            d: Dictionary of codes and details.
        """
        for k, v in d.items():
            # String keys are categories
            if isinstance(k, str):
                category = k
                for k2, v2 in v.items():
                    self._add_dictionary_key(k2, v2, category)
                continue

            # Otherwise, add directly
            self._add_dictionary_key(k, v, None)


    def load_capabilities(self, capabilities):
        """
        Update the code storage to match the monitor's reported capabilities.

        Args:
            capabilities: Capabilities object with VCP code info.
        """
        cap_codes = capabilities.get_vcp_codes()

        # Remove codes that do not exist
        for key in list(self.keys()):
            if key not in cap_codes:
                self.remove(key)

        # Process codes
        for code_i, cap_values in cap_codes.items():
            # Add codes that are in the capabilities but not already added
            code = None
            if code_i not in self:
                code = self.add(code_i)
                # code.add_name(f'Unknown Code 0x{code_i:X}')

            # Process values
            if cap_values is not None:
                if code is None:
                    code = self.get(code_i)

                for value_i in list(code.values.keys()):
                    if value_i not in cap_values:
                        code.values.remove(value_i)

                for value_i in cap_values:
                    if value_i not in code.values:
                        value = code.values.add(value_i)
                        # value.add_name(f'Unknown Value 0x{value_i:X}')


    @classmethod
    def deserialize_construct(cls, data : Dict, diff : Optional['VcpCodeStorage'] = None, instance_parent=None) -> 'VcpCodeStorage':
        """
        Construct a VcpCodeStorage from serialized data, optionally using a diff and parent.

        Args:
            data: Serialized dictionary.
            diff: Optional diff VcpCodeStorage.
            instance_parent: Optional parent for hierarchy.

        Returns:
            VcpCodeStorage: The constructed storage.
        """
        self = VcpCodeStorage(instance_parent=instance_parent)
        super(VcpCodeStorage, self).deserialize(data, diff)
        return self
