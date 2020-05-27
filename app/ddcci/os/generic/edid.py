# SPDX-License-Identifier: GPLv3-or-later
# Copyright © 2020 pyddcci Rui Pinheiro

import struct
import string
from collections import namedtuple, OrderedDict

from app.util import Namespace, HierarchicalMixin



###########
# Extended Display Identification Data class
class Edid(Namespace, HierarchicalMixin):
    EDID_FORMAT = OrderedDict([
        # ("endianness"     , ">"  ),  # big-endian
        ("header"          , "8s" ),  # constant header (8 bytes)
        ("manufacturer_id" , "H"  ),  # manufacturer ID (2 bytes)
        ("product_id"      , "H"  ),  # product ID (2 bytes)
        ("serial_number"   , "I"  ),  # serial number (4 bytes)
        ("week"            , "B"  ),  # manufacturing week (1 byte)
        ("year"            , "B"  ),  # manufacturing year (1 byte)
        ("edid_version"    , "B"  ),  # EDID version (1 byte)
        ("edid_revision"   , "B"  ),  # EDID revision (1 byte)
        ("video_input"     , "B"  ),  # video input (1 byte)
        ("horizontal"      , "B"  ),  # horizontal size (1 byte)
        ("vertical"        , "B"  ),  # vertical size (1 byte)
        ("gamma"           , "B"  ),  # display gamma (1 byte)
        ("features"        , "B"  ),  # supported features (1 byte)
        ("color"           , "10s"),  # color characteristics (10 bytes)
        ("timings"         , "3s" ),  # timings bitmap (3 bytes)
        ("timing_info"     , "16s"),  # EDID supported timings (16 bytes)
        ("descriptor1"     , "18s"),  # descriptor block 1 (18 bytes)
        ("descriptor2"     , "18s"),  # descriptor block 2 (18 bytes)
        ("descriptor3"     , "18s"),  # descriptor block 3 (18 bytes)
        ("descriptor4"     , "18s"),  # descriptor block 4 (18 bytes)
        ("extension"       , "B"  ),  # extension flag (1 byte)
        ("checksum"        , "B"  )  # checksum (1 byte)
    ])

    EDID_FORMAT_KEYS = tuple(EDID_FORMAT.keys())
    EDID_STRUCT_FORMAT = '>' + ''.join(EDID_FORMAT.values())
    EDID_STRUCT_SIZE = 128
    assert(struct.calcsize(EDID_STRUCT_FORMAT) == EDID_STRUCT_SIZE)

    UnpackedEdid = namedtuple("UnpackedEdid", tuple(EDID_FORMAT.keys()))

    def __init__(self, in_bytes, instance_parent=None):
        super().__init__(instance_parent=instance_parent)

        if in_bytes is not None:
            self.decode(in_bytes)

    def _check_checksum(self):
        # Check checksum
        if sum(map(int, self.raw)) % 256 != 0:
            raise ValueError("Checksum mismatch.")

    def _unpack(self):
        # Unpack structure
        tup = struct.unpack(self.__class__.EDID_STRUCT_FORMAT, self.raw)

        unpacked = {}
        for i, v in enumerate(tup):
            unpacked[self.__class__.EDID_FORMAT_KEYS[i]] = v

        self.unpacked = unpacked

    @staticmethod
    def parse_manufacture_id(id, swap=False):
        if swap:
            id = ((id & 0xFF) << 8) | ((id >> 8) & 0xFF)

        if id > 0b11111_11111_11111:
            raise ValueError(f"Invalid id={id}")

        id &= 0b11111_11111_11111

        ch0 = (id >> 10) & 0b11111
        ch1 = (id >>  5) & 0b11111
        ch2 = (id >>  0) & 0b11111

        return ''.join(string.ascii_uppercase[ch - 1] for ch in [ch0, ch1, ch2])

    @staticmethod
    def parse_product_id(id, swap=False):
        if swap:
            id = ((id & 0xFF) << 8) | ((id >> 8) & 0xFF)

        return id

    def _parse_type(self):
        is_digital = int(self.unpacked['video_input']) & 0b1000_0000
        # bitfield TODO
        return "digital" if is_digital else "analog"

    def _parse_size(self):
        # TODO: These can also be aspect ratios
        return {
            'width' : int(self.unpacked['horizontal']),
            'height': int(self.unpacked['vertical'  ])
        }

    def _parse_descriptor(self, descriptor):
        selector = int.from_bytes(descriptor[0:1], "big")
        if selector != 0:
            # Not a display descriptor
            return descriptor

        _type = descriptor[3]
        _bytes = descriptor[5:17]

        def _to_text():
            return _bytes.decode('cp437').split('\n', 1)[0]

        # Display serial number
        if _type == 0xFF:
            self.serial_string = _to_text()
        # Unspecified Text
        elif _type == 0xFE:
            self.unspecified_text = _to_text()
        # Display Name
        elif _type == 0xFC:
            self.display_name = _to_text()

        return {
            'type' : type,
            'bytes': _bytes
        }

    def decode(self, in_bytes):
        # Check checksum and unpack
        self.raw = in_bytes
        self._check_checksum()
        self._unpack()

        # Parse unpacked values
        self.manufacturer_id = self.__class__.parse_manufacture_id(self.unpacked['manufacturer_id'])
        self.product_id      = self.__class__.parse_product_id(self.unpacked['product_id'])
        self.serial_number   = int(self.unpacked['serial_number'])
        self.week            = int(self.unpacked['week'])
        self.year            = int(self.unpacked['year'])
        self.edid_version    = f"{self.unpacked['edid_version']}.{self.unpacked['edid_revision']}"
        self.type            = self._parse_type()
        self.size            = self._parse_size()
        self.gamma           = float(self.unpacked['gamma'] + 100) / 100
        self.features        = None  # TODO
        self.chromacity      = None  # TODO
        self.timings         = None  # TODO
        self.num_extensions  = int(self.unpacked['extension'])

        # Parse descriptors
        self.serial_string    = None
        self.unspecified_text = None
        self.display_name     = None

        self.descriptors = [
            self._parse_descriptor(self.unpacked['descriptor1']),
            self._parse_descriptor(self.unpacked['descriptor2']),
            self._parse_descriptor(self.unpacked['descriptor3']),
            self._parse_descriptor(self.unpacked['descriptor4'])
        ]

        # Clean up
        del self.raw
        del self.unpacked

        # self.log.debug(f"Decode complete: {self}")
        self.freeze_schema()
