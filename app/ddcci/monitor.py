# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Union, Hashable

from .os import OsMonitorList, OsMonitor
from .vcp.code import VcpCode
from .vcp.value import VcpValue
from .vcp.reply import VcpReply
from app.ddcci.vcp.code.code_storage import VCP_SPEC, VcpCodeStorage
from . import monitor_filter

from app.util import Namespace, LoggableMixin, HierarchicalMixin, NamedMixin


##########
# Global list of OsMonitors
OS_MONITORS = OsMonitorList('Monitors')



##########
# Monitor class
class Monitor(Namespace, LoggableMixin, HierarchicalMixin, NamedMixin):
    """
    Monitor class

    This is the 'user-visible' class. It represents a OsMonitor, given a filter.
    When it needs to operate on the OsMonitor, it will dynamically search for the OsMonitor that matches the filter.

    This allows us to configure/remember monitors independently from whether they are connected.
    It also allows us to be flexible if the monitor information changes.
    """

    VCP_CODE_TYPE = Union[VcpCode, int]
    VCP_VALUE_TYPE = Union[VcpValue, Hashable]


    def __init__(self, filter, instance_parent=None):
        filter = monitor_filter.create_monitor_filter_from(filter)

        super().__init__(instance_name=filter.get_monitor_name(prefix='', suffix=''), instance_parent=instance_parent)

        self.filter = filter

        self._codes = VCP_SPEC

        self.freeze_schema()


    # Os Monitor
    def get_os_monitor(self, enumerate=True) -> OsMonitor:
        if enumerate:
            OS_MONITORS.enumerate()

        os_monitor = self.filter.find_one(OS_MONITORS)
        if os_monitor is None:
            raise RuntimeError(f"Could not find monitor for filter '{self.filter.instance_name}'")

        return os_monitor


    # Raw VCP access
    def vcp_query_raw(self, code : int) -> VcpReply:
        return self.get_os_monitor().vcp_query(code)

    def vcp_read_raw(self, code : int) -> int:
        return self.get_os_monitor().vcp_read(code)

    def vcp_write_raw(self, code : int, value : int, verify: bool = True, timeout: int = 10) -> None:
        os_monitor = self.get_os_monitor()

        # Write
        os_monitor.vcp_write(code, value)

        if verify:
            os_monitor.verify(code, value, timeout=timeout)
        elif timeout > 0:
            os_monitor.wait_for_readable(code, timeout=timeout)


    # VCP
    @property
    def codes(self) -> VcpCodeStorage:
        return self._codes

    def _to_vcp_code(self, code: VCP_CODE_TYPE) -> VcpCode:
        if isinstance(code, VcpCode):
            return code
        return self._codes.get(code)

    @staticmethod
    def _to_vcp_value(code: VcpCode, value: VCP_VALUE_TYPE) -> VcpValue:
        if isinstance(value, VcpValue):
            return value
        return code.values.get(value)

    def vcp_query(self, code: VCP_CODE_TYPE) -> VcpReply:
        code = self._to_vcp_code(code)
        return self.vcp_query_raw(code.code)

    def vcp_read(self, code: VCP_CODE_TYPE) -> VcpValue:
        code = self._to_vcp_code(code)
        value = self.vcp_read_raw(code.code)
        return code.values.get(value)

    def vcp_write(self, code: VCP_CODE_TYPE, value: VCP_VALUE_TYPE, *args, **kwargs) -> None:
        code = self._to_vcp_code(code)
        value = self._to_vcp_value(code, value)
        self.vcp_write_raw(code.code, value.value, *args, **kwargs)

    # Magic methods (wrap VCP read/write)
    def __getitem__(self, code: VCP_CODE_TYPE):
        """ Get an attribute using dictionary syntax obj[key] """
        return self.vcp_read(code)

    def __setitem__(self, key : VCP_CODE_TYPE, value : VCP_VALUE_TYPE):
        """ Modify an attribute using dictionary syntax obj[key] = value """
        self.vcp_write(key, value)

    def __delitem__(self, key : Hashable):
        raise NotImplementedError('__del_item__ not implemented')

    def __contains__(self, key : Hashable):
        return key in self.codes
