# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

from abc import ABCMeta, abstractmethod
from .monitor_info import BaseOsMonitorInfo

from . import getLogger, Namespace
log = getLogger(__name__)



##############
# Monitor class
class BaseOsMonitor(Namespace, metaclass=ABCMeta):
    """
    Represents a monitor reported by the Operating System
    This is a base class, and should be inherited by a OS-specific class
    """

    __slots__ = Namespace.__slots__

    def __init__(self, info : BaseOsMonitorInfo, parent=None):
        super().__init__(parent=parent)

        self._set_device_info(info)
        self._initialize()

        self._connected = False
        self.on_connect()

    def _initialize(self):
        pass


    # Device Info
    @property
    def info(self):
        return self._info

    def _set_device_info(self, info : BaseOsMonitorInfo):
        self._info = info
        info.parent = self

        self.log_name = info.get_monitor_name(spaces=False)


    # Connection events
    @property
    def connected(self):
        return self._connected

    def on_connect(self):
        if self._connected:
            raise RuntimeError("Called 'on_connect' when already connected")

        self._connected = True
        self.log.info("Connected.")

    def on_disconnect(self):
        if not self._connected:
            raise RuntimeError("Called 'on_connect' when already disconnected")

        self._connected = False
        self.log.info("Disconnected.")