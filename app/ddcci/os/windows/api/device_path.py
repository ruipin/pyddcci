# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from dataclasses import dataclass

@dataclass(init=False)
class DevicePath:
    type  : str
    devid : str
    uid   : str
    guid  : str

    def __init__(self, path : str):
        super().__init__()

        self._parse(path)

    def _parse(self, path):
        """
        The device paths obtained from display_config are in the format:
            \\?\DISPLAY#<model>#<UID>#<GUID>
        """

        # Sanity check prefix, then remove it
        prefix = "\\\\?\\"
        if not path.startswith(prefix):
            raise ValueError(f"Invalid format for dev_path='{path}'. Expected it to start with '{prefix}'.")

        unprefixed_path = path[len(prefix):]

        # Split path by '#'
        split_path = unprefixed_path.split('#')
        split_len = len(split_path)
        if split_len != 4:
            raise ValueError(f"Invalid format for dev_path='{path}. Expected it to match format '{prefix}<type>#<model>#<ID>#<GUID>'")

        self.type  = split_path[0]
        self.devid = split_path[1]
        self.uid   = split_path[2]
        self.guid  = split_path[3]