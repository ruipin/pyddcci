# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from .enums import VcpCodeType

from dataclasses import dataclass

@dataclass()
class VcpReply:
    """
    Represents a response to the "Get VCP Feature & VCP Feature Reply" command defined in the DDC/CI standard.

    Contains the command code, type, current value, and maximum value for a VCP feature as reported by the monitor.
    """
    command : int
    type    : VcpCodeType
    current : int
    maximum : int