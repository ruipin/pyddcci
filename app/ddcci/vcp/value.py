# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Union, Iterable, Hashable
from ordered_set import OrderedSet

from .storage import VcpStorageStorable

from . import Namespace


class VcpValue(Namespace, VcpStorageStorable):
    """
    Class that represents a valid value for a given VcpCode, including name aliases
    """

    def __init__(self, value : int, parent):
        super().__init__(fr"VcpValue0x{value:X}", parent=parent)

        self._value = value
        self._names = OrderedSet()

        self.freeze()


    # Value
    @property
    def value(self):
        return self._value

    def vcp_storage_key(self):
        return self._value
