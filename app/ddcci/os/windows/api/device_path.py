# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from . import Namespace, getLogger

log = getLogger(__name__)


class DevicePath(Namespace):
    def __init__(self, path : str, parent=None):
        super().__init__(path, parent=parent)

        self.path = path
        self._parse()

    def _parse(self):
        """
        The device paths obtained from display_config are in the format:
            \\?\DISPLAY#<model>#<UID>#<GUID>
        """

        # Sanity check prefix, then remove it
        prefix = "\\\\?\\"
        if not self.path.startswith(prefix):
            raise ValueError(f"Invalid format for dev_path='{self.path}'. Expected it to start with '{prefix}'.")

        unprefixed_path = self.path[len(prefix):]

        # Split path by '#'
        split_path = unprefixed_path.split('#')
        split_len = len(split_path)
        if split_len != 4:
            raise ValueError(f"Invalid format for dev_path='{self.path}. Expected it to match format '{prefix}<type>#<model>#<ID>#<GUID>'")

        self.type  = split_path[0]
        self.devid = split_path[1]
        self.uid   = split_path[2]
        self.guid  = split_path[3]