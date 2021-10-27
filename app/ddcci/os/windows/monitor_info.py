# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

from ..monitor_info import BaseOsMonitorInfo

from .api import display_config, display_devices
from .api.device_path import DevicePath
from .api.edid import edid_from_monitor_model_and_uid, OSEdidError
from app.ddcci.os.generic.edid import Edid


########
# OS Monitor Information
class WindowsOsMonitorInfo(BaseOsMonitorInfo):
    """
    Windows implementation of BaseOsMonitorInfo
    """

    # Initialization
    def __init__(self, dcp_info):
        # Initialize adapter device
        adapter_device_name = str(dcp_info.source)
        adapter_device_name_prefix = r'\\.\DISPLAY'
        assert(adapter_device_name.startswith(adapter_device_name_prefix))
        adapter_device_number = int(adapter_device_name[len(adapter_device_name_prefix):])
        adapter_device_id = fr"{dcp_info.adapter.type}\{dcp_info.adapter.devid}"
        adapter_device = self.__class__.Device(name=adapter_device_name, number=adapter_device_number, id=adapter_device_id)

        # Initialize adapter
        adapter = self.__class__.Adapter(**{
            'type'  : dcp_info.adapter.type,
            'uid'   : dcp_info.adapter.uid,
            'guid'  : dcp_info.adapter.guid,
            'device': adapter_device
        })

        # Initialize monitor
        monitor_device = self.__class__.Device(id=fr"MONITOR\{dcp_info.monitor.devid}")

        monitor = self.__class__.Monitor(**{
            'type'  : dcp_info.monitor.type,
            'model' : dcp_info.monitor.devid,
            'uid'   : dcp_info.monitor.uid,
            'guid'  : dcp_info.monitor.guid,
            'device': monitor_device
        })

        if dcp_info.target['flags']['edidIdsValid']:
            monitor.manufacturer_id = Edid.parse_manufacture_id(dcp_info.target['edidManufactureId'], swap=True)
            monitor.product_id      = Edid.parse_product_id(dcp_info.target['edidProductCodeId'], swap=True)

        if dcp_info.target['flags']['friendlyNameFromEdid'] and not dcp_info.target['flags']['friendlyNameForced']:
            monitor.name = str(dcp_info.target['monitorFriendlyDeviceName'])

        # Call superclass
        super().__init__(adapter, monitor)


    def _post_initialize(self):
        super()._post_initialize()

        self._read_edid()
        self._read_GetMonitorInfo_adapter()
        self._read_GetMonitorInfo_monitor()


    # Edid
    def _read_edid(self):
        try:
            edid = edid_from_monitor_model_and_uid(self.monitor.model, self.monitor.uid)
        except OSEdidError:
            self.log.warn(f"Could not find EDID")
            return

        # Copy interesting data
        def _copy_from_edid(attr1, attr2=None):
            if attr2 is None:
                attr2 = attr1

            self_attr = getattr(self.monitor, attr1)
            edid_attr = edid[attr2]

            if self_attr is not None:
                if self_attr != edid_attr:
                    raise RuntimeError(f"Had {attr1}='{self_attr}' but got EDID.{attr2}='{edid_attr}'")
            else:
                setattr(self.monitor, attr1, edid_attr)

        _copy_from_edid('manufacturer_id')
        _copy_from_edid('product_id')
        _copy_from_edid('name', 'display_name')
        _copy_from_edid('serial', 'serial_string')


    # GetMonitorInfo
    def _read_GetMonitorInfo_adapter(self):
        i = 0
        while True:
            res = display_devices.win32_enum_display_devices_w(None, i)
            if res is None:
                raise RuntimeError(f"Could not get the adapter info from GetMonitorInfo for monitor '{self.adapter.device.name}'")

            if self.adapter.device.name == res.DeviceName and self.adapter.device.id == res.DeviceID:
                break

            i += 1

        # Copy interesting data
        def _copy(obj, attr_x, y):
            x = getattr(obj, attr_x)
            if x is not None and x != y:
                raise RuntimeError(f"Had {attr_x}='{x}', but got '{y}'")
            setattr(obj, attr_x, y)

        _copy(self.adapter, 'model', str(res.DeviceString))
        _copy(self.adapter, 'primary', res.primary)

    def _read_GetMonitorInfo_monitor(self):
        i = 0
        while True:
            res = display_devices.win32_enum_display_devices_w(self.adapter.device.name, i, flags=display_devices.EDD_GET_DEVICE_INTERFACE_NAME)
            if res is None:
                raise RuntimeError(f"Could not get the monitor info from GetMonitorInfo for monitor '{self._instance_name}'")

            res_id = DevicePath(res.DeviceID)
            if res_id.type == self.monitor.type and res_id.devid == self.monitor.model and res_id.uid == self.monitor.uid and res_id.guid == self.monitor.guid:
                break

            i += 1

        # Sanity checks
        def _assert_startswith(x, attr_y, y):
            if not str(y).startswith(x):
                raise RuntimeError(f"Expected res.{attr_y} to start with '{x}', but got '{y}'")

        device_name_prefix = fr"{self.adapter.device.name}\Monitor"
        _assert_startswith(device_name_prefix, 'DeviceName', res.DeviceName)

        # Copy interesting data
        def _copy(obj, attr_x, y):
            x = getattr(obj, attr_x)
            if x is not None and x != y:
                raise RuntimeError(f"Had {attr_x}='{x}', but got '{y}'")
            setattr(obj, attr_x, y)

        _copy(self.monitor.device, 'name', str(res.DeviceName))
        _copy(self.monitor.device, 'number', int(self.monitor.device.name[len(device_name_prefix):]))


    # Enumerate monitors
    @classmethod
    def enumerate(cls):
        paths = display_config.query_display_config(paths_only=True)

        ret = []
        for path in paths:
            info = cls(path)
            ret.append(info)

        return ret
