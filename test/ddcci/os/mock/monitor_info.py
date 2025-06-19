# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

"""
Mock implementation of BaseOsMonitorInfo for use in OS-related unit tests in pyddcci.
Provides mock monitor information and utilities for generating mock monitors.
"""

import logging
logging.getLogger('faker').setLevel(logging.ERROR)

from faker import Faker
from string import ascii_uppercase

from app.ddcci.os.monitor_info import BaseOsMonitorInfo


########
# OS Monitor Information
class MockOsMonitorInfo(BaseOsMonitorInfo):
    """
    Mock implementation of BaseOsMonitorInfo
    """

    # Initialization
    def __init__(self, mock_monitor : 'MockMonitorData'):
        # Call superclass
        super().__init__(mock_monitor.adapter, mock_monitor.monitor)


    # Enumerate monitors
    @classmethod
    def enumerate(cls):
        ret = []

        for mock_monitor in MOCK_MONITORS:
            info = MockOsMonitorInfo(mock_monitor)
            ret.append(info)

        return ret


WindowsOsMonitorInfo = MockOsMonitorInfo



#######################
# Monitors to mock
MOCK_MONITORS = []
fake = Faker()

class MockMonitorData(object):
    def __init__(self, number : int):
        # Adapter
        self.adapter_number = number

        self.adapter_device = BaseOsMonitorInfo.Device(
            id      = fake.bothify(text='PCI\VEN_##??&DEV_#?##&SUBSYS_#?####??&REV_?#', letters=ascii_uppercase),
            name    = fr'\\.\DISPLAY{number}',
            number  = self.adapter_number
        )

        self.adapter = BaseOsMonitorInfo.Adapter(
            device  = self.adapter_device,
            guid    = '{' + fake.uuid4() + '}',
            model   = ' '.join([x.capitalize() for x in fake.words(nb=3)]),
            name    = None,
            primary = False,
            type    = 'PCI',
            uid     = fake.lexify(text='?????????????')
        )

        # Monitor
        self.monitor_number = fake.random_digit()
        self.monitor_manufacturer = fake.lexify(text='???', letters=ascii_uppercase)
        self.monitor_model = self.monitor_manufacturer + fake.numerify(text='####')

        self.monitor_device = BaseOsMonitorInfo.Device(
            id      = fr'MONITOR\{self.monitor_model}',
            name    = fr'\\.\DISPLAY{number}\Monitor{self.monitor_number}',
            number  = self.monitor_number
        )

        self.monitor = BaseOsMonitorInfo.Monitor(
            device          = self.monitor_device,
            guid            = '{' + fake.uuid4() + '}',
            manufacturer_id = self.monitor_manufacturer,
            model           = self.monitor_model,
            name            = ' '.join([x.capitalize() for x in fake.words(nb=3)]),
            product_id      = fake.random_number(digits=4, fix_len=True),
            serial          = fake.md5()[0:10].upper(),
            type            = 'DISPLAY',
            uid             = fake.lexify(text='?????????????')
        )


def generate_mock_monitors(number, seed):
    Faker.seed(seed)

    global MOCK_MONITORS
    MOCK_MONITORS = []
    for i in range(1, number+1):
        MOCK_MONITORS.append(MockMonitorData(i))