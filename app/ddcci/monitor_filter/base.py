# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import List, Optional, Dict
from abc import ABCMeta, abstractmethod

from ..os import OsMonitor, OsMonitorList

from app.util import NamespaceMap, LoggableMixin, HierarchicalMixin, NamedMixin


#############
# Base class
class BaseMonitorFilter(NamespaceMap, LoggableMixin, HierarchicalMixin, NamedMixin, metaclass=ABCMeta):
    """
    Abstract base class for filtering OsMonitor objects.

    Subclasses implement match() to select monitors based on criteria. Used for monitor selection in pyddcci.
    Provides serialization, naming, and logging support.
    """
    FILTER_TYPES = {}


    # Filtering
    @abstractmethod
    def match(self, os_monitor : OsMonitor) -> bool:
        """
        Determine if the given OS monitor matches this filter.

        Args:
            os_monitor: The OS monitor to check.

        Returns:
            bool: True if the monitor matches, False otherwise.
        """
        pass

    def find(self, os_monitor_list : OsMonitorList) -> List[OsMonitor]:
        """
        Find all OS monitors in the list that match this filter.

        Args:
            os_monitor_list: List of OS monitors to search.

        Returns:
            list: All matching OS monitors.
        """
        match = []

        for os_monitor in os_monitor_list:
            if self.match(os_monitor):
                match.append(os_monitor)

        return match

    def find_one(self, os_monitor_list : OsMonitorList) -> Optional[OsMonitor]:
        """
        Find a single OS monitor in the list that matches this filter.

        Args:
            os_monitor_list: List of OS monitors to search.

        Returns:
            OsMonitor or None: The matching monitor, or None if not found or ambiguous.
        """
        match = self.find(os_monitor_list)
        len_match = len(match)

        if len_match == 0:
            return None

        if len_match > 1:
            msg = '\n\t'.join([x.instance_name for x in match])
            self.log.warning(f"Found more than one monitor, returning the first match. The following monitors matched this filter:\n\t{msg}")

        return match[0]


    # Naming
    @abstractmethod
    def get_monitor_name(self, prefix='<', suffix='>') -> str:
        """
        Get a display name for the monitor(s) selected by this filter.

        Args:
            prefix: Optional prefix for the name.
            suffix: Optional suffix for the name.

        Returns:
            str: The display name.
        """
        pass


    # Serialization
    def serialize(self) -> Dict:
        """
        Serialize this filter to a dictionary.

        Returns:
            dict: The serialized filter.
        """
        raise NotImplementedError()

    @classmethod
    def deserialize(cls, data : Dict, instance_parent=None) -> 'BaseMonitorFilter':
        """
        Deserialize a dictionary into a filter instance.

        Args:
            data: Dictionary containing serialized filter data.
            instance_parent: Optional parent instance for hierarchical filters.

        Returns:
            BaseMonitorFilter: The deserialized filter instance.

        Raises:
            ValueError: If the dictionary does not contain a 'type' key or the type is invalid.
        """
        if 'type' not in data:
            raise ValueError(f"'data' dictionary must contain key 'type'")

        data = dict(data)
        typ = data.pop('type')

        _cls = cls.FILTER_TYPES.get(typ, None)
        if _cls is None:
            raise ValueError(f"Invalid filter type {typ}")

        return _cls.deserialize(data, instance_parent=instance_parent)