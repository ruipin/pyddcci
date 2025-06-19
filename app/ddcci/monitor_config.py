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

    Args:
        filter: Monitor filter (dict or BaseMonitorFilter).
        instance_parent: Optional parent for hierarchy.
    """
    def __init__(self, filter : Union[Dict, BaseMonitorFilter], instance_parent=None, **kwargs):
        super().__init__(instance_parent=instance_parent)

        self.merge(kwargs)
        self.filter = filter


    # Filter
    @property
    def filter(self) -> BaseMonitorFilter:
        """
        Get the filter object for this config entry.
        Returns:
            BaseMonitorFilter: The filter object.
        """
        return self._filter
    @filter.setter
    def filter(self, new_filter : Union[Dict, BaseMonitorFilter]):
        """
        Set the filter for this config entry.
        Args:
            new_filter: The new filter (dict or BaseMonitorFilter).
        """
        if isinstance(new_filter, Dict):
            new_filter = BaseMonitorFilter.deserialize(new_filter, instance_parent=self)
        self._filter : BaseMonitorFilter = new_filter


    def get_os_monitor(self, enumerate=True):
        """
        Return the OS monitor matching this config entry's filter.
        Args:
            enumerate: If True, refresh the OS monitor list before searching.
        Returns:
            OsMonitor: The matched OS monitor object.
        """
        if enumerate:
            OS_MONITORS.enumerate()

        return self.filter.find_one(OS_MONITORS)

    def match(self, os_monitor):
        """
        Check if the given OS monitor matches this config entry's filter.
        Args:
            os_monitor: The OS monitor to check.
        Returns:
            bool: True if the monitor matches, False otherwise.
        """
        return self.filter.match(os_monitor)


    # Equality
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.filter == other.filter and self.__dict__ == other.__dict__

    def __hash__(self):
        return hash(self.filter)


    # Serialization
    def serialize(self) -> Dict:
        """
        Serialize this config entry to a dictionary.
        Returns:
            dict: The serialized representation.
        """
        out = OrderedDict()
        out['filter'] = self.filter.serialize()

        for k, v in self.items():
            out[k] = v

        return out

    @classmethod
    def deserialize(cls, data : Dict, instance_parent = None) -> 'MonitorConfigEntry':
        """
        Deserialize a config entry from a dictionary.
        Args:
            data: The dictionary to deserialize from.
            instance_parent: Optional parent for hierarchy.
        Returns:
            MonitorConfigEntry: The deserialized entry.
        """
        if not isinstance(data, dict):
            raise ValueError(f"'data' must be a dictionary")

        if 'filter' not in data:
            raise ValueError(f"'data' must contain 'filter' key")

        return cls(**data, instance_parent=instance_parent)



class MonitorConfig(NamespaceSet, LoggableMixin, HierarchicalMixin, NamedMixin):
    """
    Collection of monitor configuration entries, loaded from and saved to a YAML file.
    Provides methods for loading, saving, and managing monitor configurations.

    Args:
        file_path: Path to the YAML file.
        instance_name: Optional name for the config.
        instance_parent: Optional parent for hierarchy.
    """
    def __init__(self, file_path=os.path.join(CFG.app.dirs.data, 'monitors.yaml'), instance_name=None, instance_parent=None):
        super().__init__(instance_name=instance_name, instance_parent=instance_parent)

        self.file_path = file_path
        self.load()

    # Add
    def add(self, obj : Union[BaseMonitorFilter, OsMonitor]) -> None:
        """
        Add a monitor filter or OS monitor to the config.
        Args:
            obj: The filter or OS monitor to add.
        """
        filter = obj

        if isinstance(obj, OsMonitor):
            filter = OsMonitorMonitorFilter(obj)
        if isinstance(filter, OsMonitorMonitorFilter):
            filter = filter.to_monitor_info_filter()

        entry = MonitorConfigEntry(filter, instance_parent=self)
        super().add(entry)

    def get(self, obj : Union[BaseMonitorFilter, OsMonitor], add : bool = True) -> Optional[MonitorConfigEntry]:
        """
        Get the config entry for a given filter or OS monitor.
        Args:
            obj: The filter or OS monitor to look up.
            add: If True, add the entry if not found.
        Returns:
            MonitorConfigEntry or None: The found entry, or None if not found and add is False.
        """
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
        """
        Load config entries from a list of dictionaries.
        Args:
            lst: List of dictionaries to load from.
        """
        if not isinstance(lst, list):
            raise ValueError(f"'lst' must be a list")

        for d in lst:
            super().add(MonitorConfigEntry.deserialize(d, instance_parent=self))


    def load(self) -> None:
        """
        Load the monitor configuration from the YAML file.
        """
        if self.file_path is None or not os.path.exists(self.file_path):
            return

        with open(self.file_path, 'r') as file:
            yaml_l = yaml.load(file, Loader=yaml.FullLoader)

        if yaml_l is not None:
            self.load_from_list(yaml_l)


    # Saving
    def serialize(self) -> List:
        """
        Serialize all config entries to a list of dictionaries.
        Returns:
            list: The serialized config entries.
        """
        out = []

        for entry in self:
            out.append(entry.serialize())

        return out


    def yaml_str(self) -> str:
        """
        Get the YAML string representation of the config.
        Returns:
            str: The YAML string.
        """
        return yaml.dump(self.serialize())


    def save(self):
        """
        Save the monitor configuration to the YAML file.
        """
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