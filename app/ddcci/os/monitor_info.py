# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from abc import ABCMeta, abstractmethod

from . import getLogger, Namespace
log = getLogger(__name__)


class BaseOsMonitorInfo(Namespace, metaclass=ABCMeta):
    """
    Class that represents information about a given Monitor as supplied by the OS
    This is a base class, and should be inherited by a OS-specific class
    """

    class SubInfo(Namespace):
        DEFAULT_TO_NONE = True
        FIELDS = ()

        def __eq__(self, other: 'BaseOsMonitorInfo.SubInfo'):
            if self is other: return True

            for k in self:
                self_v  = self[k]
                other_v = other[k]

                if k in (self.__class__.FIELDS_NOT_NONE or ()) and self_v is None or other_v is None:
                    continue

                if self_v != other_v:
                    return False

            return True

    class Adapter(SubInfo):
        FIELDS_NOT_NONE = ('type', 'uid', 'guid', 'device')
        FIELDS          = ('name', 'model', 'primary')

    class Monitor(SubInfo):
        FIELDS_NOT_NONE = ('type', 'model', 'uid', 'guid', 'device')
        FIELDS          = ('name', 'manufacturer_id', 'product_id', 'serial')

    class Device(SubInfo):
        FIELDS_NOT_NONE = ('id',)
        FIELDS          = ('name', 'number')


    # Constructor
    def __init__(self, adapter : Adapter, monitor : Monitor, *args, **kwargs):

        super().__init__(f"{monitor.model}/{monitor.uid}")

        self.adapter = adapter
        self.adapter.parent = self

        self.monitor = monitor
        self.monitor.parent = self

        self._post_initialize(*args, **kwargs)
        self.freeze()


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

        with self.unfreeze(temporary=True):
            self._dict = dict(other._dict)


    # Enumerate monitors
    @classmethod
    @abstractmethod
    def enumerate(cls):
        pass
