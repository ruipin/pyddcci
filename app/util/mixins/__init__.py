# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

import re
def shorten_name(input : str) -> str:
    # Assume camelcase
    res = re.sub('[^A-Z0-9]', '', input)
    if res:
        return res

    # Otherwise, do nothing
    return input


# Import mixins
from .named import NamedMixin
from .hierarchical import HierarchicalMixin
from .loggable import LoggableMixin

# Create short-hands
class HierarchicalNamedMixin(HierarchicalMixin, NamedMixin):
    pass

class LoggableHierarchicalMixin(LoggableMixin, HierarchicalMixin):
    pass

class LoggableNamedMixin(LoggableMixin, NamedMixin):
    pass

class LoggableHierarchicalNamedMixin(LoggableMixin, HierarchicalMixin, NamedMixin):
    pass