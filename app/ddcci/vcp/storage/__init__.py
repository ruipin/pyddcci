# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Union, NewType, TypeVar

T_VcpStorageKey  = int
T_VcpStorageName = str
T_VcpStorageIdentifier = Union[T_VcpStorageName, T_VcpStorageKey]
T_VcpStorageStandardIdentifier = NewType('T_VcpStorageStandardIdentifier', T_VcpStorageIdentifier)

from .storable import VcpStorageStorable
T_VcpStorageStorable = TypeVar('T_VcpStorageStorable', bound=VcpStorageStorable, covariant=True)

from .storage import VcpStorage
from .storage_with_fallback import VcpStorageWithFallback
from .fallback_storable import FallbackVcpStorageStorable