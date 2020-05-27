# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

import string

from .. import BaseOsMonitor

from . import Namespace, getLogger

log = getLogger(__name__)


class OsMonitorCapabilities(Namespace):
    def __init__(self, capability_string : str, instance_parent : BaseOsMonitor):
        super().__init__("Capabilities", instance_parent=instance_parent)

        self._parse(capability_string)


    # VCP Codes
    def iter_vcp_codes(self):
        vcp = self.get('vcp', None)
        if vcp is None:
            return

        for code in self.vcp:
            if isinstance(code, tuple):
                yield code[0], code[1]

            else:
                yield code, None

    def get_vcp_codes(self):
        return [code for code in self.iter_vcp_codes()]


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
        should_split = False

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

            cur.append(accum)

            while next_depth < depth:
                depth, cur = stack.pop()

        # Copy to self
        for k, lst in result_list:
            if len(lst) == 1:
                lst = lst[0]
            self[k] = lst


    def _parse(self, capability_string):
        if capability_string is None:
            raise ValueError(f"'capability_string' must not be None")

        self.raw = capability_string

        # Split by parentheses
        self._parse_parentheses(capability_string)
