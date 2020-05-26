# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from enum import Enum
from . import Namespace, getLogger

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


class VcpReply(Namespace):
    """
    Represents a response to the "Get VCP Feature & VCP Feature Reply" command defined in the DDC/CI standard
    """

    __slots__ = Namespace.__slots__

    FIELDS_NOT_NONE = ('command', 'type', 'current', 'maximum')

    def __init__(self, command : int, *, type : VcpCodeType, current : int, maximum : int):
        super().__init__(f"Vcp{hex(command)}Reply", command=command, type=type, current=current, maximum=maximum)