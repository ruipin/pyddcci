# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Union, NewType, Dict

from .os import OS_MONITORS, OsMonitor
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
# Monitor class
class Monitor(Namespace, LoggableMixin, HierarchicalMixin, NamedMixin):
    """
    User-facing monitor class for DDC/CI control.

    Represents a logical monitor, selected by a filter, and provides methods to query and set VCP codes and values.
    Handles dynamic association with OS monitors and supports configuration persistence.

    Args:
        filter: Monitor selector or filter object.
        instance_parent: Optional parent for hierarchy.
    """


    def __init__(self, filter, instance_parent=None):
        filter = monitor_filter.create_monitor_filter_from(filter)

        super().__init__(instance_name=filter.get_monitor_name(prefix='', suffix=''), instance_parent=instance_parent)

        self.filter = filter

        self._codes = None

        self.freeze_schema()


    # Os Monitor
    def get_os_monitor(self, enumerate=True) -> OsMonitor:
        """
        Return the OS monitor object matching this monitor's filter.
        Args:
            enumerate: If True, refresh the OS monitor list before searching.
        Returns:
            OsMonitor: The matched OS monitor object.
        Raises:
            RuntimeError: If no monitor matches the filter.
        """
        if enumerate:
            OS_MONITORS.enumerate()

        os_monitor = self.filter.find_one(OS_MONITORS)
        if os_monitor is None:
            raise RuntimeError(f"Could not find monitor for filter '{self.filter.instance_name}'")

        return os_monitor

    def load_capabilities(self) -> None:
        """
        Load and apply monitor VCP capabilities from the OS monitor.
        """
        self.codes.load_capabilities(self.get_os_monitor().capabilities)


    # Codes
    @property
    def codes(self):
        """
        Get the VCP code storage for this monitor, loading from config or spec as needed.
        Returns:
            VcpCodeStorage: The code storage object for this monitor.
        """
        if self._codes is None:
            try:
                imported_codes = False
                if CFG.monitors.codes.automatic_import:
                    imported_codes = self.import_codes()

                if not imported_codes:
                    self._codes = VcpCodeStorage(instance_parent=self)
                    self._codes.copy_storage(vcp_spec.VCP_SPEC)

                    if CFG.monitors.capabilities.automatic:
                        self.load_capabilities()
            except AttributeError as e:
                raise RuntimeError() from e

        return self._codes

    def _export_codes(self) -> Dict:
        return self.codes.serialize(diff=vcp_spec.VCP_SPEC)

    def export_codes(self) -> None:
        """
        Export the current VCP code configuration to the monitor config file.
        """
        from .monitor_config import MONITOR_CONFIG
        cfg = MONITOR_CONFIG.get(self.filter, add=True)
        cfg['codes'] = self._export_codes()
        MONITOR_CONFIG.save()

    def _import_codes(self, data : Dict) -> None:
        self._codes = VcpCodeStorage.deserialize_construct(data, diff=vcp_spec.VCP_SPEC, instance_parent=self)

    def import_codes(self) -> bool:
        """
        Import VCP code configuration for this monitor from the config file.
        Returns:
            bool: True if codes were imported, False otherwise.
        """
        from .monitor_config import MONITOR_CONFIG

        cfg = MONITOR_CONFIG.get(self.filter, add=False)

        if cfg is None:
            cfg = MONITOR_CONFIG.get(self.get_os_monitor(), add=False)

        if cfg is None:
            return False

        if 'codes' not in cfg:
            return False

        self._import_codes(cfg['codes'])
        return True





    # Raw VCP access
    def vcp_query_raw(self, code : int) -> VcpReply:
        """
        Query a VCP code using the raw integer code value.
        Args:
            code: The VCP code as an integer.
        Returns:
            VcpReply: The reply from the monitor.
        """
        return self.get_os_monitor().vcp_query(code)

    def vcp_read_raw(self, code : int) -> int:
        """
        Read a VCP code value using the raw integer code value.
        Args:
            code: The VCP code as an integer.
        Returns:
            int: The value read from the monitor.
        """
        return self.get_os_monitor().vcp_read(code)

    def vcp_write_raw(self, code : int, value : int, verify: bool = True, timeout: int = 10) -> None:
        """
        Write a value to a VCP code using the raw integer code value.
        Args:
            code: The VCP code as an integer.
            value: The value to write.
            verify: Whether to verify the value after writing.
            timeout: Timeout for verification/readiness.
        """
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
        """
        Query a VCP code using a code identifier (alias or int).
        Args:
            code_id: The VCP code identifier (alias or int).
        Returns:
            VcpReply: The reply from the monitor.
        """
        code = self._to_vcp_code(code_id)
        return self.vcp_query_raw(code.code)

    def vcp_read(self, code_id: T_VcpCodeIdentifier) -> VcpValue:
        """
        Read a VCP code value using a code identifier (alias or int).
        Args:
            code_id: The VCP code identifier (alias or int).
        Returns:
            VcpValue: The value read from the monitor.
        """
        code = self._to_vcp_code(code_id)
        value = self.vcp_read_raw(code.code)
        return code[value]

    def vcp_write(self, code_id: T_VcpCodeIdentifier, value_id: T_VcpValueIdentifier, *args, **kwargs) -> None:
        """
        Write a value to a VCP code using code and value identifiers (alias or int).
        Args:
            code_id: The VCP code identifier (alias or int).
            value_id: The value identifier (alias or int).
        """
        code = self._to_vcp_code(code_id)
        value = self._to_vcp_value(code, value_id)
        self.vcp_write_raw(code.code, value.value, *args, **kwargs)


    # Magic methods (wrap VCP read/write)
    def __getitem__(self, code_id: T_VcpCodeIdentifier) -> VcpValue:
        """
        Get a VCP value using dictionary syntax: monitor[code_id].
        Args:
            code_id: The VCP code identifier.
        Returns:
            VcpValue: The value read from the monitor.
        """
        return self.vcp_read(code_id)

    def __setitem__(self, code_id : T_VcpCodeIdentifier, value_id : T_VcpValueIdentifier) -> None:
        """
        Set a VCP value using dictionary syntax: monitor[code_id] = value_id.
        Args:
            code_id: The VCP code identifier.
            value_id: The value identifier.
        """
        self.vcp_write(code_id, value_id)

    def __delitem__(self, code_id : T_VcpCodeIdentifier) -> None:
        raise NotImplementedError('__del_item__ not implemented')

    def __contains__(self, code_id : T_VcpCodeIdentifier):
        """
        Check if a VCP code exists for this monitor.
        Args:
            code_id: The VCP code identifier.
        Returns:
            bool: True if the code exists, False otherwise.
        """
        return code_id in self._get_read_only_codes()
