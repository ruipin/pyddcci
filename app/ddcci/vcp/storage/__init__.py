# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Union, TypeVar

T_VcpStorageKey  = int
T_VcpStorageName = str

# Can't use NewType on Union types, so we define them directly
T_VcpStorageIdentifier = Union[T_VcpStorageName, T_VcpStorageKey]

from .storable import VcpStorageStorable

from .storage import VcpStorage