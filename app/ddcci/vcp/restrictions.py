# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from . import CFG, Namespace, getLogger

log = getLogger(__name__)


class VcpCodeRestrictions(Namespace):
    """
    Class that represents the restrictions there can be on the value of a VCP.
    For continuous VCPs,
    """

