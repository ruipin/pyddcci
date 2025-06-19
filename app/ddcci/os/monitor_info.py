# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from abc import ABCMeta, abstractmethod

from typing import Optional
from dataclasses import dataclass, fields
from app.util import NamespaceMap, LoggableHierarchicalMixin


class BaseOsMonitorInfo(NamespaceMap, LoggableHierarchicalMixin, metaclass=ABCMeta):
    """
    Base class representing information about a monitor as supplied by the OS.
    Should be subclassed for OS-specific implementations. Contains nested dataclasses for device, adapter, and monitor info.
    """

    class SubInfo:
        def __eq__(self, other):
            for f in fields(self):
                v_self  = getattr(self, f.name)
                v_other = getattr(other, f.name)

                if v_self is None or v_other is None:
                    continue

                if v_self != v_other:
                    return False
            return True

        def __ne__(self, other):
            return not self.__eq__(other)

        def items(self):
            for f in fields(self):
                yield f.name, getattr(self, f.name)

    @dataclass(eq=False, order=False)
    class Device(SubInfo):
        id     : str
        name   : Optional[str] = None
        number : Optional[int] = None

    @dataclass(eq=False, order=False)
    class Adapter(SubInfo):
        type   : str
        uid    : str
        guid   : str
        device : 'BaseOsMonitorInfo.Device'
        name   : Optional[str]  = None
        model  : Optional[str]  = None
        primary: Optional[bool] = None

    @dataclass(eq=False, order=False)
    class Monitor(SubInfo):
        type            : str
        uid             : str
        guid            : str
        device          : 'BaseOsMonitorInfo.Device'
        name            : Optional[str] = None
        model           : Optional[str]  = None
        manufacturer_id : Optional[int] = None
        product_id      : Optional[int] = None
        serial          : Optional[str] = None



    # Constructor
    def __init__(self, adapter : Adapter, monitor : Monitor, *args, **kwargs):

        super().__init__()

        self.adapter = adapter
        self.adapter.instance_parent = self

        self.monitor = monitor
        self.monitor.instance_parent = self

        self._post_initialize(*args, **kwargs)
        self.freeze_schema()


    def _post_initialize(self, *args, **kwargs):
        pass


    # Get name
    def get_monitor_name(self, delimiter='/', spaces=True):
        arr = []

        if self.adapter.name is not None:
            arr += [self.adapter.name]
        else:
            arr += [self.adapter.model]

        if self.monitor.name is not None:
            arr += [self.monitor.name]
        else:
            arr += [self.monitor.model]

        if self.monitor.serial is not None:
            arr += [self.monitor.serial]
        else:
            arr += [self.monitor.uid]

        res = delimiter.join(arr)
        if not spaces:
            res = res.replace(' ', '')

        assert res
        return res


    # Comparison
    def represents_same_monitor(self, other : 'BaseOsMonitorInfo'):
        if self is other: return True

        if self.adapter != other.adapter: return False
        if self.monitor != other.monitor: return False

        return True


    def update(self, other : 'BaseOsMonitorInfo'):
        assert(self.represents_same_monitor(other))

        with self.unfreeze_schema(temporary=True):
            self.__dict__ = dict(other.__dict__)


    # Enumerate monitors
    @classmethod
    @abstractmethod
    def enumerate(cls):
        pass
