# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from typing import Any, Dict, Union

from .value import VcpValue
from ..storage import VcpStorage, T_VcpStorageIdentifier


class VcpValueStorage(VcpStorage):
    def _create_value(self, value : int) -> VcpValue:
        return VcpValue(value, instance_parent=self)



    # Import / Export
    def export(self, diff : 'VcpValueStorage' = None) -> Union[Dict, str]:
        if diff is None:
            return self.asdict()

        d = self.asdict(recursive=False)
        d_diff = diff.asdict(recursive=False)
        res = {}

        def _add_default(value_i):
            if 'default' not in res:
                res['default'] = str(value_i)
            else:
                res['default'] += f',{value_i}'

        # remove values that match
        for value_i, value_obj in d.items():
            if value_i not in d_diff:
                value_d = value_obj.export()
                if len(value_d) != 0:
                    res[value_i] = value_d
                else:
                    _add_default(value_i)
                continue

            value_d = value_obj.export(diff=d_diff[value_i])

            if len(value_d) > 0:
                res[value_i] = value_d
            else:
                _add_default(value_i)

        if 'default' in res and len(res) == 1:
            res = res['default']

        return res
