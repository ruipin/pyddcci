# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

import os
os.environ['PYDDCCI_LOGGING_LEVELS_TTY'] = 'DEBUG'

import test.ddcci.os.mock
from .testcase import TestCase