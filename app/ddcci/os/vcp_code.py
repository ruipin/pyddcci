# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Union, Dict, Any, Optional

from .monitor import BaseOsMonitor

from abc import ABCMeta, abstractmethod

from enum import Enum
from . import Namespace, Sequence, getLogger

log = getLogger(__name__)


class VcpControlType(Enum):
    # Controls that accept only specific values.
    # The valid values of these controls do not need to be continuous in value.
    # Non-continuous controls can be “read and write”, “read-only”or “write-only”
    VCP_NON_CONTINUOUS = 0

    # Controls that accept any value from zero to a maximum value specific for each control.
    # All continuous controls are read and write enabled.
    VCP_CONTINUOUS = 1

class VcpCodeType(Enum):
    # Momentary VCP code. Sending a command of this type causes the monitor to initiate a self-timed operation and then revert to its original state.
    # Examples include display tests and degaussing.
    VCP_MOMENTARY     = 0

    # Set Parameter VCP code. Sending a command of this type changes some aspect of the monitor's operation.
    VCP_SET_PARAMETER = 1


class VcpQuery(Namespace):
    __slots__ = Namespace.__slots__

    def __init__(self, vcp_code : 'BaseOsVcpCode', *, typ : VcpCodeType, value : int, maximum : int):
        super().__init__(f"{vcp_code.log_name}Query")

        self.vcp_code = vcp_code
        self.type     = typ
        self.value    = value
        self.maximum  = maximum


class BaseOsVcpCode(Namespace, metaclass=ABCMeta):
    """
    Virtual Control Panel Code
    This is a base class, and should be inherited by a OS-specific class
    """

    __slots__ = Namespace.__slots__

    def __init__(self, command : int, typ : Optional[VcpCodeType] = None, description : str = None, parent=None, aliases : Optional[Dict[Any, int]] = None):
        super().__init__(f"VCP{command}", parent=parent)

        self._command = command
        self.type = typ
        self.description = description

        self._value_aliases = aliases or {}


    # Value Aliases
    def translate_to_value(self, value : Any) -> int:
        alias = self._value_aliases.get(value, None)
        if alias is not None:
            return alias

        if not isinstance(value, int):
            raise ValueError(f"value='{value}' did not match any alias and is not an integer")

        return value

    def add_value_alias(self, alias : Any, value : int) -> None:
        if not isinstance(value, int):
            raise ValueError(f"value='{value}' must be an integer")

        if alias is None:
            raise ValueError(f"'alias' must not be None")

        self._value_aliases[alias] = value


    # Read
    @abstractmethod
    def _read(self, monitor : BaseOsMonitor) -> VcpQuery:
        pass

    def read(self, monitor) -> VcpQuery:
        mthd = getattr(monitor, 'get_os_monitor')
        if callable(mthd):
            monitor = mthd()

        return self._read(monitor)


    # Write
    @abstractmethod
    def _write(self, monitor : BaseOsMonitor, value : int) -> None:
        pass

    def write(self, monitor, value : int) -> None:
        mthd = getattr(monitor, 'get_os_monitor')
        if callable(mthd):
            monitor = mthd()

        return self._write(monitor, value)


    # Properties
    @property
    def command(self):
        return self._command
