# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

import time
from typing import Optional

from abc import ABCMeta, abstractmethod
from .monitor_info import BaseOsMonitorInfo
from app.ddcci.vcp.reply import VcpReply

from app.util import Namespace, LoggableHierarchicalNamedMixin, CFG


##############
# VcpError exception class
class VcpError(RuntimeError):
    pass


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

    def query_capabilities(self):
        cache = CFG.monitors.capabilities.cache

        cap_str = None
        if cache:
            from ..monitor_config import MONITOR_CONFIG
            cfg = MONITOR_CONFIG.get(self, add=False)
            if cfg is not None:
                cap_str = cfg.get('capabilities', None)
                self.log.debug("Loaded monitor capabilities from cache")

        if not cap_str:
            self.log.info("Querying monitor capabilities... (may take a few seconds)")
            cap_str = self._get_capabilities_string()

            if cache:
                from ..monitor_config import MONITOR_CONFIG
                cfg = MONITOR_CONFIG.get(self, add=True)
                cfg['capabilities'] = cap_str
                MONITOR_CONFIG.save()
                self.log.debug("Saved monitor capabilities to cache")


        from .generic.capabilities import OsMonitorCapabilities
        capabilities = OsMonitorCapabilities(cap_str, instance_parent=self)
        self._capabilities = capabilities

    @property
    def capabilities(self):
        if self._capabilities is None:
            self.query_capabilities()

        return self._capabilities


    # VCP Query
    @abstractmethod
    def _vcp_query(self, code : int) -> VcpReply:
        pass

    def vcp_query(self, code : int) -> VcpReply:
        # self.log.debug(f"VCP Query: 0x{code:X}")
        try:
            return self._vcp_query(code)
        except Exception as e:
            raise VcpError(f"Failed to query VCP Code 0x{code:X}") from e

    # VCP Read
    def _vcp_read(self, code : int) -> int:
        return self._vcp_query(code).current

    def vcp_read(self, code : int) -> int:
        # self.log.debug(f"VCP Read: 0x{code:X}")
        try:
            return self._vcp_read(code)
        except OSError as e:
            raise VcpError(f"Failed to read VCP Code 0x{code:X}") from e

    # VCP Write
    @abstractmethod
    def _vcp_write(self, code : int, value: int) -> None:
        pass

    def vcp_write(self, code : int, value: int) -> None:
        # self.log.debug(f"VCP Write: 0x{code:X} <= 0x{value:X}")
        try:
            self._vcp_write(code, value)
        except OSError as e:
            raise VcpError(f"Failed to write VCP 0x{code:X} <= 0x{value:X}") from e

    def verify(self, code: int, value: Optional[int], timeout: int):
        if value is None:
            wait_msg = f"Waiting for VCP 0x{code:X} to become readable..."
        else:
            wait_msg = f"Waiting for VCP 0x{code:X} == 0x{value:X}..."

        for i in range(timeout, 0, -1):
            msg = f"{i:2}s - {wait_msg}"

            try:
                new_val = self.vcp_read(code)
                if i != timeout: self.log.debug(f"{msg} Read 0x{new_val:X}.")

                if value is None:
                    self.log.debug(f"VCP 0x{code:X} is readable again.")
                    break
                elif new_val == value:
                    self.log.debug(f"Verified 0x{code:X} == 0x{new_val:X}.")
                    break
            except VcpError:
                self.log.debug(f"{msg} Read failed.")

            time.sleep(1)
        else:
            raise VcpError(f"Timeout verifying VCP 0x{code:X}")

    def wait_for_readable(self, code: int, timeout: int):
        self.verify(code, None, timeout)

    # Connection events
    @property
    def connected(self):
        return self._connected

    def on_connect(self):
        if self._connected:
            raise RuntimeError("Called 'on_connect' when already connected")

        self._connected = True
        self.log.debug("Connected.")


    def on_disconnect(self):
        if not self._connected:
            raise RuntimeError("Called 'on_connect' when already disconnected")

        self._connected = False
        self.log.debug("Disconnected.")