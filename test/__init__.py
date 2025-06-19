# SPDX-License-Identifier: GPLv3
# Copyright © 2020 pyddcci Rui Pinheiro

"""
Test package initializer for pyddcci.
Sets up the test environment and imports base test utilities and mocks.
"""

import os
os.environ['PYDDCCI_LOGGING_LEVELS_TTY'] = 'DEBUG'

import test.ddcci.os.mock
from .testcase import TestCase