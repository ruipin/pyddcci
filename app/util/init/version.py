# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

import os
import subprocess


# Implementation
VERSION = "0.1"

def git_revision():
    """
    Get the current git revision string, if available.
    Returns:
        str or None: The git revision string, or None if not available.
    """
    def _minimal_ext_cmd(cmd):
        # construct minimal environment
        env = {}
        for k in ['SYSTEMROOT', 'PATH']:
            v = os.environ.get(k)
            if v is not None:
                env[k] = v

        # LANGUAGE is used on win32
        env['LANGUAGE'] = 'C'
        env['LANG'] = 'C'
        env['LC_ALL'] = 'C'

        _out = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env).communicate()
        if _out[1]:
            return None
        return _out[0]

    rev = None

    try:
        out = _minimal_ext_cmd([
                'git', 'describe',
                '--exclude', '*',
                '--always',
                '--broken',
                '--dirty',
                '--abbrev=9'
            ])

        if out is None:
            return None

        rev = out.strip().decode('ascii')

    except OSError:
        pass

    return rev
GIT_REVISION = git_revision()


def get_version_string():
    """
    Get the full version string, including git revision if available.
    Returns:
        str: The version string.
    """
    ver = VERSION

    if GIT_REVISION:
        ver += "-" + GIT_REVISION

    return ver
VERSION_STRING = get_version_string()
