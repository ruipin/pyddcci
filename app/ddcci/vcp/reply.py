# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from .enums import VcpCodeType
from . import Namespace


class VcpReply(Namespace):
    """
    Represents a response to the "Get VCP Feature & VCP Feature Reply" command defined in the DDC/CI standard
    """

    FIELDS_NOT_NONE = ('command', 'type', 'current', 'maximum')

    def __init__(self, command : int, *, type : VcpCodeType, current : int, maximum : int):
        super().__init__(f"Vcp{hex(command)}Reply", command=command, type=type, current=current, maximum=maximum)