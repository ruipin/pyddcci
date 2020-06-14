# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

from .. import BaseOsMonitor

from app.util.namespace import NamespaceMap
from app.util.mixins import LoggableMixin, HierarchicalMixin, NamedMixin


class OsMonitorCapabilities(NamespaceMap, LoggableMixin, HierarchicalMixin, NamedMixin):
    def __init__(self, capability_string : str, instance_parent : BaseOsMonitor):
        super().__init__(instance_name="Capabilities", instance_parent=instance_parent)

        self._parse(capability_string)


    # VCP Codes
    def iter_vcp_codes(self):
        vcp = self.get('vcp', None)
        if vcp is None:
            return

        return vcp.items()

    def get_vcp_codes(self):
        return self.get('vcp', None)


    # Parsing
    def _parse_parentheses(self, text):
        text = text.strip()
        if text.startswith('('):
            text = text[1:]
        if text.endswith(')'):
            text = text[:-1]

        split = []
        accum = ''
        depth = 0

        # Split parentheses into
        for ch in text:
            if ch == '(':
                split.append((depth, accum.strip()))
                depth += 1
                accum = ''
                continue

            elif ch == ')':
                split.append((depth, accum.strip()))
                accum = ''
                depth -= 1
                continue

            elif ch == ' ':
                split.append((depth, accum.strip()))
                accum = ''
                continue

            accum += ch

        if depth != 0:
            raise ValueError("Unbalanced parentheses")

        # Collect into list of lists
        stack = []
        result_list = []
        cur = result_list

        split_len = len(split)

        for i in range(0, split_len):
            depth, accum  = split[i]
            next_depth, _ = split[i+1] if i < split_len-1 else (0, None)

            if next_depth > depth:
                arr = []
                cur.append((accum, arr))
                stack.append((depth, cur))
                cur = arr
                continue

            if len(accum) > 0:
                cur.append(accum)

            while next_depth < depth:
                depth, cur = stack.pop()

        # Copy to self
        for k, lst in result_list:
            if len(lst) == 1:
                lst = lst[0]
            self[k] = lst


    def _process_vcp_codes(self):
        vcp = self.get('vcp', None)
        if vcp is None:
            return

        vcp_out = {}

        for code in self.vcp:
            if isinstance(code, tuple):
                values = []
                for val in code[1]:
                    values.append(int(val, 16))

                vcp_out[int(code[0], 16)] = values

            else:
                vcp_out[int(code, 16)] = None

        self.vcp = vcp_out


    def _parse(self, capability_string):
        if capability_string is None:
            raise ValueError(f"'capability_string' must not be None")

        self.raw = capability_string

        # Split by parentheses
        self._parse_parentheses(capability_string)

        # Post-process VCP codes
        self._process_vcp_codes()