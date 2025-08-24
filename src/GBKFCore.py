#!/usr/bin/python3

#
# This file is part of gbkf-core-python.
#
# Copyright (c) 2025 Rafael Senties Martinelli.
#
# Licensed under the Privative-Friendly Source-Shared License (PFSSL) v1.0.
# You may use, modify, and distribute this file under the terms of that license.
#
# This software is provided "as is", without warranty of any kind.
# The authors are not liable for any damages arising from its use.
#
# See the LICENSE file for more details.

from enum import IntEnum


class Header:
    GBKF_KEYWORD = b"gbkf"
    GBKF_KEYWORD_SIZE = 4

    GBKF_VERSION_START = GBKF_KEYWORD_SIZE
    GBKF_VERSION_SIZE = 1

    SPECIFICATION_ID_START = GBKF_VERSION_START + GBKF_VERSION_SIZE
    SPECIFICATION_SIZE = 4

    SPECIFICATION_VERSION_START = SPECIFICATION_ID_START + SPECIFICATION_SIZE
    SPECIFICATION_VERSION_SIZE = 2

    KEYS_SIZE_START = SPECIFICATION_VERSION_START + SPECIFICATION_VERSION_SIZE
    KEYS_SIZE_SIZE = 1

    KEYED_VALUES_NB_START = KEYS_SIZE_START + KEYS_SIZE_SIZE
    KEYED_VALUES_NB_SIZE = 4

    SIZE = KEYED_VALUES_NB_START + KEYED_VALUES_NB_SIZE


class ValueType(IntEnum):
    BLOB = 1
    BOOLEAN = 2

    STRING = 10

    INT8 = 20
    INT32 = 21
    INT16 = 22
    INT64 = 23

    UINT8 = 30
    UINT16 = 31
    UINT32 = 33
    UINT64 = 34

    FLOAT32 = 40
    FLOAT64 = 41

class ValueTypeBoundaries:
    _uint_8_max = 255
    _uint_16_max = 65_535
    _uint_32_max = 4_294_967_295
    _uint_64_max = 18_446_744_073_709_551_615

    _int_8_min = -128
    _int_8_max = 127
    _int_16_min = -32_768
    _int_16_max = 32_767
    _int_32_min = -2_147_483_648
    _int_32_max = 2_147_483_647
    _int_64_min = -9_223_372_036_854_775_808
    _int_64_max = 9_223_372_036_854_775_807

    _single_size = 4
    _single_max = 3.4028235e+38

    _double_size = 8  # IEEE 754 double-precision
    _double_max = 1.7976931348623157e+308

    _sha256_size = 32


class KeyedEntry:

    def __init__(self, value_type:ValueType):
        self.instance_id = 0
        self.__type = value_type
        self.__values = []

    def get_type(self):
        return self.__type

    def add_value(self, value):
        self.__values.append(value)

    def add_values(self, values):
        self.__values.extend(values)

    def get_values(self):
        return self.__values