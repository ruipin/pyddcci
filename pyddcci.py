# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

import sys
from app.util import CFG, getLogger


if __name__ == "__main__":
    log = getLogger(CFG.app.name)

    log.info("Starting.")
    log.debug('Cmdline= %s', ' '.join(sys.argv))
    CFG.debug()


    from app.ddcci.vcp.code.code_storage import VcpCodeStorage, VCP_SPEC

    second = VcpCodeStorage(instance_name='second')
    second.fallback = VCP_SPEC



    print(repr(second['input']))
    print(repr(second['contrast']))

    second['banana'] = 0x1
    print(repr(second['banana']))
    assert not VCP_SPEC.contains('banana')

    second['contrast']['50PCT'] = 50
    print(repr(second['contrast']['50PCT']))
    assert not VCP_SPEC['contrast'].contains('50PCT')

    VCP_SPEC['contrast']['25PCT'] = 25
    print(repr(VCP_SPEC['contrast']['25PCT']))
    print(repr(second['contrast']['25PCT']))

    second['contrast']['25PCT'] = None
    assert VCP_SPEC['contrast'].contains('25PCT')
    assert not second['contrast'].contains('25PCT')


    exit()


    from app.ddcci.monitor import Monitor
    monitor = Monitor('Primary')

    monitor['input'] = 'dp1'

    prev = monitor['input']
    log.info(f"Previous Input: {prev}")

    monitor['input'] = 'HDMI 1'
    log.info(f"Switched to {monitor['input']}")

    monitor['input'] = prev
    log.info(f"Back to {monitor['input']}")