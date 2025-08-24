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

import struct
from hashlib import sha256

import GBKFCore


class GBKFCoreReader:

    def __init__(self, read_path: str):

        self.__bytes_data = None
        self.__gkbf_version = None
        self.__specification_id = None
        self.__specification_version = None
        self.__keys_size = None
        self.__keyed_values_nb = None

        with open(read_path, "rb") as file:
            self.__bytes_data = file.read()

        self.__sha256_read = self.__bytes_data[-GBKFCore.ValueTypeBoundaries._sha256_size:]
        self.__sha256_calculated = sha256(self.__bytes_data[:-GBKFCore.ValueTypeBoundaries._sha256_size]).digest()

        self.read_header()

    def read_header(self):

        if len(self.__bytes_data) < GBKFCore.Header.SIZE:
            raise ValueError("Header too short")

        if self.__bytes_data[0:GBKFCore.Header.GBKF_KEYWORD_SIZE] != GBKFCore.Header.GBKF_KEYWORD:
            raise ValueError("Invalid start keyword")

        self.__gkbf_version, _ = self.__read_int(GBKFCore.Header.GBKF_VERSION_START,
                                                 size=GBKFCore.Header.GBKF_VERSION_SIZE,
                                                 signed=False)

        self.__specification_id, _ = self.__read_int(GBKFCore.Header.SPECIFICATION_ID_START,
                                                     size=GBKFCore.Header.SPECIFICATION_SIZE,
                                                     signed=False)

        self.__specification_version, _ = self.__read_int(GBKFCore.Header.SPECIFICATION_VERSION_START,
                                                          size=GBKFCore.Header.SPECIFICATION_VERSION_SIZE,
                                                          signed=False)

        self.__keys_size, _ = self.__read_int(GBKFCore.Header.KEYS_SIZE_START,
                                              size=GBKFCore.Header.KEYS_SIZE_SIZE,
                                              signed=False)

        self.__keyed_values_nb, _ = self.__read_int(GBKFCore.Header.KEYED_VALUES_NB_START,
                                                    size=GBKFCore.Header.KEYED_VALUES_NB_SIZE,
                                                    signed=False)

    def verifies_sha(self):
        return self.__sha256_read == self.__sha256_calculated

    def get_gbkf_version(self) -> None | int:
        return self.__gkbf_version

    def get_specification_id(self) -> None | int:
        return self.__specification_id

    def get_specification_version(self) -> None | int:
        return self.__specification_version

    def get_keys_size(self) -> None | int:
        return self.__keys_size

    def get_keyed_values_nb(self) -> None | int:
        return self.__keyed_values_nb

    def get_keyed_values(self) -> dict[str, list[GBKFCore.KeyedEntry]]:

        keyed_values = {}

        current_pos = GBKFCore.Header.SIZE
        for _ in range(self.__keyed_values_nb):

            key, current_pos = self.__read_ascii(current_pos, self.__keys_size)
            instance_id, current_pos = self.__read_int(current_pos, size=4, signed=False)
            values_number, current_pos = self.__read_int(current_pos, size=4, signed=False)
            value_type, current_pos = self.__read_int(current_pos, size=1, signed=False)

            keyed_entry = GBKFCore.KeyedEntry(GBKFCore.ValueType(value_type))
            keyed_entry.instance_id = instance_id

            match value_type:

                case GBKFCore.ValueType.INT8:
                    values, current_pos = self.__read_values_int(current_pos, values_number, 1, signed=True)

                case GBKFCore.ValueType.INT16:
                    values, current_pos = self.__read_values_int(current_pos, values_number, 2, signed=True)

                case GBKFCore.ValueType.INT32:
                    values, current_pos = self.__read_values_int(current_pos, values_number, 4, signed=True)

                case GBKFCore.ValueType.INT64:
                    values, current_pos = self.__read_values_int(current_pos, values_number, 8, signed=True)

                case GBKFCore.ValueType.UINT8:
                    values, current_pos = self.__read_values_int(current_pos, values_number, 1, signed=False)

                case GBKFCore.ValueType.UINT16:
                    values, current_pos = self.__read_values_int(current_pos, values_number, 2, signed=False)

                case GBKFCore.ValueType.UINT32:
                    values, current_pos = self.__read_values_int(current_pos, values_number, 4, signed=False)

                case GBKFCore.ValueType.UINT64:
                    values, current_pos = self.__read_values_int(current_pos, values_number, 8, signed=False)

                case GBKFCore.ValueType.FLOAT32:
                    values, current_pos = self.__read_values_float32(current_pos, values_number)

                case GBKFCore.ValueType.FLOAT64:
                    values, current_pos = self.__read_values_float64(current_pos, values_number)

                case _:
                    raise ValueError("Unknown keyed value type")

            keyed_entry.add_values(values)

            if key in keyed_values:
                keyed_values[key].append(keyed_entry)
            else:
                keyed_values[key] = [keyed_entry]

        return keyed_values

    def __read_int(self, start_pos: int, size: int, signed:bool) -> tuple[int, int]:
        end_pos = start_pos + size
        bytes_value = self.__bytes_data[start_pos:end_pos]
        return int.from_bytes(bytes_value, byteorder='little', signed=signed), end_pos

    def __read_ascii(self, start_pos: int, length: int) -> tuple[str, int]:
        end_pos = start_pos + length
        bytes_value = self.__bytes_data[start_pos:end_pos]
        return bytes_value.decode('ascii'), end_pos

    def __read_single(self, start_pos: int) -> tuple[str, float]:
        end_pos = start_pos + GBKFCore.ValueTypeBoundaries._single_size
        single_bytes = self.__bytes_data[start_pos:end_pos]
        return struct.unpack('>f', single_bytes)[0], end_pos

    def __read_double(self, start_pos: int) -> tuple[str, float]:
        end_pos = start_pos + GBKFCore.ValueTypeBoundaries._double_size
        double_bytes = self.__bytes_data[start_pos:end_pos]
        return struct.unpack('>d', double_bytes)[0], end_pos

    def __read_values_int(self,
                          start_pos: int,
                          values_nb: int,
                          integers_size: int,
                          signed: bool) -> tuple[tuple[int, ...], int]:

        current_pos = start_pos
        values = []

        for _ in range(values_nb):
            value, current_pos = self.__read_int(current_pos, integers_size, signed=signed)
            values.append(value)

        return tuple(values), current_pos

    def __read_values_float32(self, start_pos: int, values_nb: int) -> tuple[tuple[float, ...], int]:

        values = []
        current_pos = start_pos
        for _ in range(values_nb):
            value, current_pos = self.__read_single(current_pos)
            values.append(value)

        return tuple(values), current_pos

    def __read_values_float64(self, start_pos: int, values_nb: int) -> tuple[tuple[float, ...], int]:

        values = []
        current_pos = start_pos
        for _ in range(values_nb):
            value, current_pos = self.__read_double(current_pos)
            values.append(value)

        return tuple(values), current_pos
