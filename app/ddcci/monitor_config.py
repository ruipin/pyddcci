# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

import os
import oyaml as yaml

from typing import List, Dict, Union, Optional
from collections import OrderedDict

from app.util import CFG, NamespaceSet, NamespaceMap, LoggableMixin, HierarchicalMixin, NamedMixin

from .monitor_filter import MonitorInfoMonitorFilter, OsMonitorMonitorFilter, BaseMonitorFilter
from .os import OS_MONITORS, OsMonitor



class MonitorConfigEntry(NamespaceMap, LoggableMixin, HierarchicalMixin):
    """
    Represents a single monitor configuration entry, including its filter and additional settings.
    Used for matching and managing configuration for a specific monitor.
    """
    def __init__(self, filter : Union[Dict, BaseMonitorFilter], instance_parent=None, **kwargs):
        super().__init__(instance_parent=instance_parent)

        self.merge(kwargs)
        self.filter = filter


    # Filter
    @property
    def filter(self) -> BaseMonitorFilter:
        return self._filter
    @filter.setter
    def filter(self, new_filter : Union[Dict, BaseMonitorFilter]):
        if isinstance(new_filter, Dict):
            new_filter = BaseMonitorFilter.deserialize(new_filter, instance_parent=self)
        self._filter : BaseMonitorFilter = new_filter


    def get_os_monitor(self, enumerate=True):
        if enumerate:
            OS_MONITORS.enumerate()

        return self.filter.find_one(OS_MONITORS)

    def match(self, os_monitor):
        return self.filter.match(os_monitor)


    # Equality
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.filter == other.filter and self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(self.filter)


    # Serialization
    def serialize(self) -> Dict:
        out = OrderedDict()
        out['filter'] = self.filter.serialize()

        for k, v in self.items():
            out[k] = v

        return out

    @classmethod
    def deserialize(cls, data : Dict, instance_parent = None) -> 'MonitorConfigEntry':
        if not isinstance(data, dict):
            raise ValueError(f"'data' must be a dictionary")

        if 'filter' not in data:
            raise ValueError(f"'data' must contain 'filter' key")

        return cls(**data, instance_parent=instance_parent)



class MonitorConfig(NamespaceSet, LoggableMixin, HierarchicalMixin, NamedMixin):
    """
    Collection of monitor configuration entries, loaded from and saved to a YAML file.
    Provides methods for loading, saving, and managing monitor configurations.
    """
    def __init__(self, file_path=os.path.join(CFG.app.dirs.data, 'monitors.yaml'), instance_name=None, instance_parent=None):
        super().__init__(instance_name=instance_name, instance_parent=instance_parent)

        self.file_path = file_path
        self.load()

    # Add
    def add(self, obj : Union[BaseMonitorFilter, OsMonitor]) -> None:
        filter = obj

        if isinstance(obj, OsMonitor):
            filter = OsMonitorMonitorFilter(obj)
        if isinstance(filter, OsMonitorMonitorFilter):
            filter = filter.to_monitor_info_filter()

        entry = MonitorConfigEntry(filter, instance_parent=self)
        super().add(entry)

    def get(self, obj : Union[BaseMonitorFilter, OsMonitor], add : bool = True) -> Optional[MonitorConfigEntry]:
        if isinstance(obj, OsMonitor):
            for entry in self:
                if isinstance(entry.filter, (OsMonitorMonitorFilter, MonitorInfoMonitorFilter)) and entry.match(obj):
                    return entry
        else:
            if isinstance(obj, OsMonitorMonitorFilter):
                obj = obj.to_monitor_info_filter()

            for entry in self:
                if entry.filter == obj:
                    return entry

        if add:
            self.add(obj)
            entry = self.get(obj, add=False)
            if entry is None:
                raise RuntimeError("'entry' should never be None")
            return entry

        return None


    # Loading
    def load_from_list(self, lst : List) -> None:
        if not isinstance(lst, list):
            raise ValueError(f"'lst' must be a list")

        for d in lst:
            super().add(MonitorConfigEntry.deserialize(d, instance_parent=self))


    def load(self) -> None:
        if self.file_path is None or not os.path.exists(self.file_path):
            return

        with open(self.file_path, 'r') as file:
            yaml_l = yaml.load(file, Loader=yaml.FullLoader)

        if yaml_l is not None:
            self.load_from_list(yaml_l)


    # Saving
    def serialize(self) -> List:
        out = []

        for entry in self:
            out.append(entry.serialize())

        return out


    def yaml_str(self) -> str:
        return yaml.dump(self.serialize())


    def save(self):
        if self.file_path is None:
            return

        assert not CFG.app.test

        self.log.debug("Saving monitor configuration...")
        with open(self.file_path, 'w') as file:
            yaml_str = self.yaml_str()
            file.write(yaml_str)


###########
# Global config instance
MONITOR_CONFIG = MonitorConfig()