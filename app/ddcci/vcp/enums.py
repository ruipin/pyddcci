# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from enum import Enum



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
