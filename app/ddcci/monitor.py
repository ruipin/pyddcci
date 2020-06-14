# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Union, NewType, Dict

from .os import OsMonitorList, OsMonitor
from .vcp.code import VcpCode
from .vcp.value import VcpValue
from .vcp.reply import VcpReply
from .vcp.storage import T_VcpStorageIdentifier
from .vcp.code.code_storage import VcpCodeStorage
from .vcp import vcp_spec

from . import monitor_filter

from app.util import Namespace, LoggableMixin, HierarchicalMixin, NamedMixin, CFG

T_VcpCodeIdentifier = NewType('T_VcpCodeIdentifier', Union[VcpCode, T_VcpStorageIdentifier])
T_VcpValueIdentifier = NewType('T_VcpValueIdentifier', Union[VcpValue, T_VcpStorageIdentifier])


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


    def __init__(self, filter, instance_parent=None):
        filter = monitor_filter.create_monitor_filter_from(filter)

        super().__init__(instance_name=filter.get_monitor_name(prefix='', suffix=''), instance_parent=instance_parent)

        self.filter = filter

        self._codes = None

        self.freeze_schema()


    # Os Monitor
    def get_os_monitor(self, enumerate=True) -> OsMonitor:
        if enumerate:
            OS_MONITORS.enumerate()

        os_monitor = self.filter.find_one(OS_MONITORS)
        if os_monitor is None:
            raise RuntimeError(f"Could not find monitor for filter '{self.filter.instance_name}'")

        return os_monitor

    def load_capabilities(self) -> None:
        self.codes.load_capabilities(self.get_os_monitor().capabilities)


    # Codes
    @property
    def codes(self):
        if self._codes is None:
            self._codes = VcpCodeStorage()
            self._codes.copy_storage(vcp_spec.VCP_SPEC)

            imported_codes = False
            if CFG.monitors.codes.automatic_import:
                imported_codes = self.import_codes()

            if not imported_codes and CFG.monitors.capabilities.automatic:
                self.load_capabilities()

        return self._codes

    def export_codes(self) -> Dict:
        return self.codes.export(diff=vcp_spec.VCP_SPEC)

    def import_codes(self) -> bool:
        # TODO
        pass



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
    def _get_read_only_codes(self):
        """ Returns a VcpCodeStorage instance to be used internally and not modified """
        if self._codes is not None:
            return self.codes

        return vcp_spec.VCP_SPEC

    def _to_vcp_code(self, code_id: T_VcpCodeIdentifier) -> VcpCode:
        if isinstance(code_id, VcpCode):
            return code_id
        return self._get_read_only_codes().get(code_id)

    @staticmethod
    def _to_vcp_value(code: VcpCode, value_id: T_VcpValueIdentifier) -> VcpValue:
        if isinstance(value_id, VcpValue):
            return value_id
        return code[value_id]

    def vcp_query(self, code_id: T_VcpCodeIdentifier) -> VcpReply:
        code = self._to_vcp_code(code_id)
        return self.vcp_query_raw(code.code)

    def vcp_read(self, code_id: T_VcpCodeIdentifier) -> VcpValue:
        code = self._to_vcp_code(code_id)
        value = self.vcp_read_raw(code.code)
        return code[value]

    def vcp_write(self, code_id: T_VcpCodeIdentifier, value_id: T_VcpValueIdentifier, *args, **kwargs) -> None:
        code = self._to_vcp_code(code_id)
        value = self._to_vcp_value(code, value_id)
        self.vcp_write_raw(code.code, value.value, *args, **kwargs)


    # Magic methods (wrap VCP read/write)
    def __getitem__(self, code_id: T_VcpCodeIdentifier) -> VcpValue:
        """ Get an attribute using dictionary syntax obj[key] """
        return self.vcp_read(code_id)

    def __setitem__(self, code_id : T_VcpCodeIdentifier, value_id : T_VcpValueIdentifier) -> None:
        """ Modify an attribute using dictionary syntax obj[key] = value """
        self.vcp_write(code_id, value_id)

    def __delitem__(self, code_id : T_VcpCodeIdentifier) -> None:
        raise NotImplementedError('__del_item__ not implemented')

    def __contains__(self, code_id : T_VcpCodeIdentifier):
        return code_id in self._get_read_only_codes()
