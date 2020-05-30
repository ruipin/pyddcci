# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from ordered_set import OrderedSet

from .storage import VcpStorageStorable

from app.util import Namespace, HierarchicalMixin, NamedMixin


class VcpValue(VcpStorageStorable, Namespace, HierarchicalMixin, NamedMixin):
    """
    Class that represents a valid value for a given VcpCode, including name aliases
    """

    def __init__(self, value : int, instance_parent : HierarchicalMixin):
        super().__init__(instance_name=fr"VcpValue0x{value:X}", instance_parent=instance_parent)

        self._value = value
        self._names = OrderedSet()

        self.freeze_schema()


    # Value
    @property
    def value(self):
        return self._value

    def vcp_storage_key(self):
        return self._value