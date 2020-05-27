# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Union, Hashable, Set, Iterable

from ordered_set import OrderedSet

from .enums import VcpControlType
from .storage import VcpStorageStorable
from .value_storage import VcpValueStorage
from .value import VcpValue

from . import Namespace, getLogger

log = getLogger(__name__)


class VcpCode(Namespace, VcpStorageStorable):
    def __init__(self, code : int, parent=None):
        super().__init__(f"VcpCode0x{code:X}", parent=parent)

        self.code = code

        self._aliases = VcpValueStorage(parent=self)

        self.type = None
        self.description = None

        self.freeze()


    # Code
    def vcp_storage_key(self):
        return self.code


    # Type
    @property
    def type(self):
        return self._type
    @type.setter
    def type(self, new_value : Union[None, VcpControlType]):
        self._type = new_value


    # Aliases
    @property
    def aliases(self):
        return self._aliases

    def add_aliases(self, new_value_name : Hashable, new_value : int):
        self._values[new_value_name] = new_value


    # Restrictions
    @property
    def maximum(self) -> int:
        return self._maximum
    @maximum.setter
    def maximum(self, new_maximum):
        new_maximum = self.to_vcp_value(new_maximum)

    @property
    def allowed(self) -> Union[Set[int], range]:
        if self._type is not VcpControlType.VCP_NON_CONTINUOUS:
            return range(0, self.maximum+1)
        return self._allowed

    def is_allowed(self, value):
        value = self.get_value_for(value)
        return value in self.allowed
