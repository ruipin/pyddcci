# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro


def struct_to_dict(s):
    d = {}
    for field_tuple in s._fields_:
        field_name = field_tuple[0]

        value = getattr(s, field_name)
        if hasattr(value, '_fields_'):
            value = struct_to_dict(value)

        d[field_name] = value

    return d