# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

from abc import ABCMeta, abstractmethod
from .monitor_info import BaseOsMonitorInfo
from app.ddcci.vcp.reply import VcpReply

from app.util import Namespace, LoggableHierarchicalNamedMixin



##############
# Monitor class
class BaseOsMonitor(Namespace, LoggableHierarchicalNamedMixin, metaclass=ABCMeta):
    """
    Represents a monitor reported by the Operating System
    This is a base class, and should be inherited by a OS-specific class
    """

    def __init__(self, info : BaseOsMonitorInfo, *args, instance_parent=None, **kwargs):
        super().__init__(instance_parent=instance_parent)

        self._set_device_info(info)

        self._capabilities = None

        self._connected = False

        self._post_initialize(*args, **kwargs)

    def _post_initialize(self):
        pass


    # Device Info
    @property
    def info(self):
        return self._info

    def _set_device_info(self, info : BaseOsMonitorInfo):
        self._info = info

        info.instance_parent = self

        self.instance_name = info.get_monitor_name(spaces=False)


    # Capabilities
    @abstractmethod
    def _get_capabilities_string(self) -> str:
        pass

    def _populate_capabilities(self):
        self.log.info("Populating capabilities... (might take a few seconds)")

        cap_str = self._get_capabilities_string()

        from .generic.capabilities import OsMonitorCapabilities
        capabilities = OsMonitorCapabilities(cap_str, instance_parent=self)
        self._capabilities = capabilities

    @property
    def capabilities(self):
        if self._capabilities is None:
            self._populate_capabilities()

        return self._capabilities


    # VCP Query
    @abstractmethod
    def _vcp_query(self, code : int) -> VcpReply:
        pass

    def vcp_query(self, code : int) -> VcpReply:
        return self._vcp_query(code)

    # VCP Read
    def vcp_read(self, code : int) -> int:
        return self._vcp_query(code).current

    # VCP Write
    @abstractmethod
    def _vcp_write(self, code : int, value: int) -> None:
        pass

    def vcp_write(self, code : int, value: int) -> None:
        return self._vcp_write(code, value)


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