# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Dict, Any
from abc import ABCMeta

from app.ddcci.monitor import Monitor
from app.ddcci.monitor_filter import BaseMonitorFilter, create_monitor_filter_from

class FilterCliCommandMixin(metaclass=ABCMeta):
    """
    Mixin for CLI commands that operate on a monitor filter.
    Resolves and validates the filter argument for the command, and creates a Monitor instance.
    """
    def __init__(self, filter : BaseMonitorFilter, *args, **kwargs):
        self.filter  = filter
        self.monitor = Monitor(filter)

        super().__init__(*args, **kwargs)


    @classmethod
    def constructor_args_from_argparse(cls, filter : str, *args, **kwargs) -> Dict[str, Any]:
        d = super(FilterCliCommandMixin, cls).constructor_args_from_argparse(*args, **kwargs)

        filter = create_monitor_filter_from(filter)
        d['filter']  = filter

        return d
