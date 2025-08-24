#!/usr/bin/python3
import struct
from hashlib import sha256
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

from typing import Sequence

import GBKFCore


def verify_int(value: int, min_value: int, max_value: int):
    if not isinstance(value, int):
        raise ValueError(f"Value={value} must be an integer")

    elif value < min_value:
        raise ValueError(f"Value={value} must be greater than or equal to {min_value}")

    elif value > max_value:
        raise ValueError(f"Value={value} must be less than or equal to {max_value}")


def get_int_boundary(length: int, signed: bool, minimum: bool = False) -> int:
    """
    Returns integer boundaries based on length in bytes.

    Args:
        length (int): Number of bytes (1, 2, 4, or 8).
        signed (bool): True for signed integers, False for unsigned.
        minimum (bool): Only relevant if signed=True.
                        True = min signed int, False = max signed int.

    Returns:
        int: The boundary value.
    """
    bounds = {
        (False, False): {1: GBKFCore.ValueTypeBoundaries._uint_8_max,
                         2: GBKFCore.ValueTypeBoundaries._uint_16_max,
                         4: GBKFCore.ValueTypeBoundaries._uint_32_max,
                         8: GBKFCore.ValueTypeBoundaries._uint_64_max},
        (True, False): {1: GBKFCore.ValueTypeBoundaries._int_8_max,
                        2: GBKFCore.ValueTypeBoundaries._int_16_max,
                        4: GBKFCore.ValueTypeBoundaries._int_32_max,
                        8: GBKFCore.ValueTypeBoundaries._int_64_max},
        (True, True): {1: GBKFCore.ValueTypeBoundaries._int_8_min,
                       2: GBKFCore.ValueTypeBoundaries._int_16_min,
                       4: GBKFCore.ValueTypeBoundaries._int_32_min,
                       8: GBKFCore.ValueTypeBoundaries._int_64_min},
    }

    try:
        return bounds[(signed, minimum)][length]
    except KeyError:
        raise ValueError(f"Invalid parameters: length={length}, signed={signed}, minimum={minimum}")


class GBKFCoreWriter:

    def __init__(self):
        self.__byte_buffer = None

        self.__keys_size = 1
        self.__keyed_values_nb = 0
        self.__keys = []

        self.reset()

    def reset(self):
        self.__byte_buffer = bytearray(GBKFCore.Header.SIZE)
        self.__byte_buffer[0:GBKFCore.Header.GBKF_KEYWORD_SIZE] = GBKFCore.Header.GBKF_KEYWORD

        self.__keyed_values_nb = 0
        self.__keys = []
        self.__keys_size = 1

        self.set_gbkf_version()
        self.set_specification_id()
        self.set_specification_version()
        self.set_keys_size()
        self.set_keyed_values_nb()

    def set_gbkf_version(self, uint8: int = 1):
        self.__set_integer(uint8,
                           min_value=0,
                           max_value=GBKFCore.ValueTypeBoundaries._uint_8_max,
                           start_pos=GBKFCore.Header.GBKF_VERSION_START,
                           length=GBKFCore.Header.GBKF_VERSION_SIZE)

    def set_specification_id(self, uint32: int = 0):
        self.__set_integer(uint32,
                           min_value=0,
                           max_value=GBKFCore.ValueTypeBoundaries._uint_32_max,
                           start_pos=GBKFCore.Header.SPECIFICATION_ID_START,
                           length=GBKFCore.Header.SPECIFICATION_SIZE)

    def set_specification_version(self, uint16: int = 0):
        self.__set_integer(uint16,
                           min_value=0,
                           max_value=GBKFCore.ValueTypeBoundaries._uint_16_max,
                           start_pos=GBKFCore.Header.SPECIFICATION_VERSION_START,
                           length=GBKFCore.Header.SPECIFICATION_VERSION_SIZE)

    def set_keys_size(self, uint8: int = 1):

        if any(len(key) != uint8 for key in self.__keys):
            raise ValueError(
                f"Impossible to set keys length={uint8}, since there are already keys with another length.")

        self.__set_integer(uint8,
                           min_value=1,
                           max_value=GBKFCore.ValueTypeBoundaries._uint_8_max,
                           start_pos=GBKFCore.Header.KEYS_SIZE_START,
                           length=GBKFCore.Header.KEYS_SIZE_SIZE)

        self.__keys_size = uint8

    def set_keyed_values_nb(self, uint3: int = 0):
        self.__set_integer(uint3,
                           min_value=0,
                           max_value=GBKFCore.ValueTypeBoundaries._uint_32_max,
                           start_pos=GBKFCore.Header.KEYED_VALUES_NB_START,
                           length=GBKFCore.Header.KEYED_VALUES_NB_SIZE)

    def set_keyed_values_nb_auto(self):
        self.set_keyed_values_nb(self.__keyed_values_nb)

    def add_keyed_values_int8(self,
                               key: str,
                               instance_id: int,
                               integers: Sequence[int]):

        self.__add_keyed_values_integer(key=key,
                                        instance_id=instance_id,
                                        integers=integers,
                                        integer_type=GBKFCore.ValueType.INT8,
                                        signed=True)

    def add_keyed_values_int16(self,
                                key: str,
                                instance_id: int,
                                integers: Sequence[int]):

        self.__add_keyed_values_integer(key=key,
                                        instance_id=instance_id,
                                        integers=integers,
                                        integer_type=GBKFCore.ValueType.INT16,
                                        signed=True)

    def add_keyed_values_int32(self,
                                key: str,
                                instance_id: int,
                                integers: Sequence[int]):

        self.__add_keyed_values_integer(key=key,
                                        instance_id=instance_id,
                                        integers=integers,
                                        integer_type=GBKFCore.ValueType.INT32,
                                        signed=True)

    def add_keyed_values_int64(self,
                                key: str,
                                instance_id: int,
                                integers: Sequence[int]):

        self.__add_keyed_values_integer(key=key,
                                        instance_id=instance_id,
                                        integers=integers,
                                        integer_type=GBKFCore.ValueType.INT64,
                                        signed=True)

    def add_keyed_values_uint8(self,
                               key: str,
                               instance_id: int,
                               integers: Sequence[int]):

        self.__add_keyed_values_integer(key=key,
                                        instance_id=instance_id,
                                        integers=integers,
                                        integer_type=GBKFCore.ValueType.UINT8,
                                        signed=False)

    def add_keyed_values_uint16(self,
                                key: str,
                                instance_id: int,
                                integers: Sequence[int]):

        self.__add_keyed_values_integer(key=key,
                                        instance_id=instance_id,
                                        integers=integers,
                                        integer_type=GBKFCore.ValueType.UINT16,
                                        signed=False)

    def add_keyed_values_uint32(self,
                                key: str,
                                instance_id: int,
                                integers: Sequence[int]):

        self.__add_keyed_values_integer(key=key,
                                        instance_id=instance_id,
                                        integers=integers,
                                        integer_type=GBKFCore.ValueType.UINT32,
                                        signed=False)

    def add_keyed_values_uint64(self,
                                key: str,
                                instance_id: int,
                                integers: Sequence[int]):

        self.__add_keyed_values_integer(key=key,
                                        instance_id=instance_id,
                                        integers=integers,
                                        integer_type=GBKFCore.ValueType.UINT64,
                                        signed=False)

    def add_keyed_values_float32(self, key: str, instance_id: int, singles: Sequence[float]):

        line_bytes = self.__get_keyed_values_header(key=key,
                                                    instance_id=instance_id,
                                                    values_nb=len(singles),
                                                    values_type=GBKFCore.ValueType.FLOAT32)

        for single in singles:
            line_bytes += self.__format_single(single)

        self.__byte_buffer += line_bytes
        self.__keyed_values_nb += 1

        if key not in self.__keys:
            self.__keys.append(key)

    def add_keyed_values_float64(self, key: str, instance_id: int, doubles: Sequence[float]):

        line_bytes = self.__get_keyed_values_header(key=key,
                                                    instance_id=instance_id,
                                                    values_nb=len(doubles),
                                                    values_type=GBKFCore.ValueType.FLOAT64)

        for double in doubles:
            line_bytes += self.__format_double(double)

        self.__byte_buffer += line_bytes
        self.__keyed_values_nb += 1

        if key not in self.__keys:
            self.__keys.append(key)

    def write(self, write_path: str, auto_update: bool = True, add_footer: bool = True):

        if auto_update:
            self.set_keyed_values_nb_auto()

        with open(write_path, "wb") as f:
            f.write(self.__byte_buffer)

        if add_footer:
            #
            # The footer must be added by separate, or it will bug in case of multiple writes.
            #
            with open(write_path, "ab") as f:
                footer_hash = sha256(self.__byte_buffer).digest()
                f.write(footer_hash)

    def __format_key(self, key: str):

        if key == "":
            raise ValueError("Key cannot be empty.")

        elif len(key) != self.__keys_size:
            raise ValueError(f"The key={key} does not match the keys length={self.__keys_size}")

        return key.encode('ascii')

    @staticmethod
    def __format_integer(value: int, size: int, signed:bool):

        if signed:
            if value < get_int_boundary(size, signed=signed, minimum=True):
                raise ValueError(f"Integer out of minimum bonds.")

        elif value < 0:
            raise ValueError("An Un-signed Integer cannot be negative")

        if value > get_int_boundary(size, signed=signed, minimum=False):
            raise ValueError(f"Integer out of maximum bonds.")


        return value.to_bytes(size, byteorder='little', signed=signed)

    @staticmethod
    def __format_single(value: float):

        # if value < 0:
        #     raise ValueError("Integer cannot be negative")
        #
        if value > GBKFCore.ValueTypeBoundaries._single_max:  # Todo  why this is not working?
            raise ValueError(f"Single {value} > {GBKFCore.ValueTypeBoundaries._single_max}")

        return struct.pack('>f', value)

    @staticmethod
    def __format_double(value: float):

        # if value < 0:
        #     raise ValueError("Integer cannot be negative")
        #
        if value > GBKFCore.ValueTypeBoundaries._double_max:  # Todo  why this is not working?
            raise ValueError(f"Double {value} > {GBKFCore.ValueTypeBoundaries._double_max}")

        return struct.pack('>d', value)

    def __set_integer(self,
                      value: int,
                      min_value: int,
                      max_value: int,
                      start_pos: int,
                      length: int):
        verify_int(value, min_value=min_value, max_value=max_value)
        binary_value = value.to_bytes(length, byteorder='little', signed=False)
        self.__byte_buffer[start_pos:start_pos + length] = binary_value

    def __get_keyed_values_header(self,
                                  key: str,
                                  instance_id: int,
                                  values_nb: int,
                                  values_type: GBKFCore.ValueType) -> bytearray:

        try:
            GBKFCore.ValueType(values_type)
        except ValueError:
            raise ValueError(f"Un-valid KeyedValues.Type={values_type}")

        line_bytes = bytearray()
        line_bytes += self.__format_key(key)
        line_bytes += self.__format_integer(instance_id, size=4, signed=False)
        line_bytes += self.__format_integer(values_type, size=1, signed=False)
        line_bytes += self.__format_integer(values_nb, size=4, signed=False)

        return line_bytes

    def __add_keyed_values_integer(self,
                                   key: str,
                                   instance_id: int,
                                   integers: Sequence[int],
                                   integer_type: GBKFCore.ValueType,
                                   signed:bool):

        values_nb = len(integers)

        # Set the header
        line_bytes = self.__get_keyed_values_header(key=key,
                                                    instance_id=instance_id,
                                                    values_nb=values_nb,
                                                    values_type=integer_type)

        # Set the integers length
        match integer_type:
            case GBKFCore.ValueType.UINT8 | GBKFCore.ValueType.INT8:
                integers_size = 1

            case GBKFCore.ValueType.UINT16 | GBKFCore.ValueType.INT16:
                integers_size = 2

            case GBKFCore.ValueType.UINT32 | GBKFCore.ValueType.INT32:
                integers_size = 4

            case GBKFCore.ValueType.UINT64 | GBKFCore.ValueType.INT64:
                integers_size = 8

            case _:
                raise ValueError(f"Unsupported integer Type")


        # Set the values
        for integer in integers:
            line_bytes += self.__format_integer(value=integer, size=integers_size, signed=signed)

        # Add to the buffer
        self.__byte_buffer += line_bytes
        self.__keyed_values_nb += 1

        if key not in self.__keys:
            self.__keys.append(key)
