#!/usr/bin/python3

#
#  Copyright (C) 2025 Rafael Senties Martinelli. All Rights Reserved.
#

import struct
from hashlib import sha256
from typing import Sequence

def verify_int(value:int, min_value:int, max_value:int):

    if not isinstance(value, int):
        raise ValueError(f"Value={value} must be an integer")

    elif value < min_value:
        raise ValueError(f"Value={value} must be greater than or equal to {min_value}")

    elif value > max_value:
        raise ValueError(f"Value={value} must be less than or equal to {max_value}")

def get_uint_length(value:int) -> int:

    if value < 0:
        raise ValueError(f"Integer={value} must be greater than or equal to 0")

    bytes_length = (value.bit_length() + 7) // 8

    if bytes_length in (1,2):
        return bytes_length

    elif bytes_length <= 4: # in case of 3, 4
        return 4

    elif bytes_length <= 8:  # in case of 5, 6, 7, 8
        return 8

    raise ValueError(f"Integer={value} is too big, it should be at maximum 8 bytes")

def get_uint_max(length:int) -> int:
    """
        This function should be studied to target performance
    """
    match length:
        case 1:
            return Constants._uint_8_max
        case 2:
            return Constants._uint_16_max
        case 4:
            return Constants._uint_64_max
        case 8:
            return Constants._uint_64_max

    raise ValueError(f"Value={length} must be 1,2,4,8.")


class Constants:

    _uint_8_max = 255
    _uint_16_max = 65_535
    _uint_32_max = 4_294_967_295
    _uint_64_max = 18_446_744_073_709_551_615

    _single_length = 4
    _single_max = 3.4028235e+38

    _double_length = 8 # IEEE 754 double-precision
    _double_max = 1.7976931348623157e+308

    _sha256_length = 32

    class Header:

        _start_keyword = b"gbkf"
        _start_keyword_length = len(_start_keyword)

        _gbkf_version_start = _start_keyword_length
        _gbkf_version_length = 1

        _specification_id_start = _gbkf_version_start + _gbkf_version_length
        _specification_id_length = 4

        _specification_version_start = _specification_id_start + _specification_id_length
        _specification_version_length = 2

        _keys_length_start = _specification_version_start + _specification_version_length
        _keys_length_length = 1

        _keyed_values_nb_start = _keys_length_start + _keys_length_length
        _keyed_values_nb_length = 4

        _length = _keyed_values_nb_start + _keyed_values_nb_length

    class KeyedValues:
        _instance_id_length = 4
        _values_nb_length = 4
        _values_type_length = 1

        _integers_length_length = 1

        class Types:
            _undefined = 0
            _integer = 1
            _single = 2
            _double = 3

            _all = (_undefined, _integer, _single, _double)

class Reader:

    def __init__(self, read_path:str):

        self.__bytes_data = None
        self.__gkbf_version = None
        self.__specification_id = None
        self.__specification_version = None
        self.__keys_length = None
        self.__keyed_values_nb = None

        with open(read_path, "rb") as file:
            self.__bytes_data = file.read()

        self.__sha256_read = self.__bytes_data[-Constants._sha256_length:]
        self.__sha256_calculated = sha256(self.__bytes_data[:-Constants._sha256_length]).digest()

        self.read_header()

    def read_header(self):

        if len(self.__bytes_data) < Constants.Header._length:
            raise ValueError("Header too short")

        start_keyword = self.__bytes_data[0:Constants.Header._start_keyword_length]
        if start_keyword != Constants.Header._start_keyword:
            raise ValueError("File is not gbkf")

        self.__gkbf_version, _ = self.__read_int(Constants.Header._gbkf_version_start,
                                                 Constants.Header._gbkf_version_length)

        self.__specification_id, _ = self.__read_int(Constants.Header._specification_id_start,
                                                     Constants.Header._specification_id_length)

        self.__specification_version, _ = self.__read_int(Constants.Header._specification_version_start,
                                                          Constants.Header._specification_version_length)

        self.__keys_length, _ = self.__read_int(Constants.Header._keys_length_start,
                                                Constants.Header._keys_length_length)

        self.__keyed_values_nb, _ = self.__read_int(Constants.Header._keyed_values_nb_start,
                                                    Constants.Header._keyed_values_nb_length)

    def verifies_sha(self):
        return self.__sha256_read == self.__sha256_calculated

    def get_gbkf_version(self) -> None | int:
        return self.__gkbf_version

    def get_specification_id(self) -> None | int:
        return self.__specification_id

    def get_specification_version(self) -> None | int:
        return self.__specification_version

    def get_keys_length(self) -> None | int:
        return self.__keys_length

    def get_keyed_values_nb(self) -> None | int:
        return self.__keyed_values_nb

    def get_keyed_values(self) -> {}:
        """
            Return a dictionary containing:
                {"key":[
                    (Instance ID, Values Nb, Values Type, [Values]),
                ]}
        """

        keyed_values = {}

        current_pos = Constants.Header._length
        for _ in range(self.__keyed_values_nb):

            key, current_pos = self.__read_ascii(current_pos, self.__keys_length)
            instance_id, current_pos = self.__read_int(current_pos, Constants.KeyedValues._instance_id_length)
            values_number, current_pos = self.__read_int(current_pos, Constants.KeyedValues._values_nb_length)
            value_type, current_pos = self.__read_int(current_pos, Constants.KeyedValues._values_type_length)

            match value_type:
                # case Constants.KeyedValues.Types._undefined:
                #     values = tuple()

                case Constants.KeyedValues.Types._integer:
                    values, current_pos = self.__read_line_int(current_pos, values_number)

                case Constants.KeyedValues.Types._single:
                    values, current_pos = self.__read_line_single(current_pos, values_number)

                case Constants.KeyedValues.Types._double:
                    values, current_pos = self.__read_line_double(current_pos, values_number)

                case _:
                    raise ValueError("Unknown keyed value type")

            if key in keyed_values:
                keyed_values[key].append((instance_id, values_number, value_type, values))
            else:
                keyed_values[key] = [(instance_id, values_number, value_type, values)]


        return keyed_values

    def __read_int(self, start_pos:int, length:int) -> (int, int):
        end_pos = start_pos + length
        bytes_value = self.__bytes_data[start_pos:end_pos]
        return int.from_bytes(bytes_value, byteorder='big', signed=False), end_pos

    def __read_ascii(self, start_pos:int, length:int) -> (str, int):
        end_pos = start_pos + length
        bytes_value = self.__bytes_data[start_pos:end_pos]
        return bytes_value.decode('ascii'), end_pos

    def __read_single(self, start_pos:int)  -> (str, float):
        end_pos = start_pos + Constants._single_length
        single_bytes = self.__bytes_data[start_pos:end_pos]
        return struct.unpack('>f', single_bytes)[0], end_pos

    def __read_double(self, start_pos:int)  -> (str, float):
        end_pos = start_pos + Constants._double_length
        double_bytes = self.__bytes_data[start_pos:end_pos]
        return struct.unpack('>d', double_bytes)[0], end_pos

    def __read_line_int(self, start_pos:int, values_nb:int) -> ([int], int):

        integers_length, current_pos = self.__read_int(start_pos, Constants.KeyedValues._integers_length_length)

        values = []
        for _ in range(values_nb):
            value, current_pos = self.__read_int(current_pos, integers_length)
            values.append(value)

        return tuple(values), current_pos

    def __read_line_single(self, start_pos:int, values_nb:int) -> ([float], int):

        values = []
        current_pos = start_pos
        for _ in range(values_nb):
            value, current_pos = self.__read_single(current_pos)
            values.append(value)

        return tuple(values), current_pos

    def __read_line_double(self, start_pos:int, values_nb:int) -> ([float], int):

        values = []
        current_pos = start_pos
        for _ in range(values_nb):
            value, current_pos = self.__read_double(current_pos)
            values.append(value)

        return tuple(values), current_pos


class Writer:

    def __init__(self):
        self.__byte_buffer = None

        self.__keys_length = 1
        self.__keyed_values_nb = 0
        self.__keys = []

        self.reset()

    def reset(self):
        self.__byte_buffer = bytearray(Constants.Header._length)
        self.__byte_buffer[0:Constants.Header._start_keyword_length] = Constants.Header._start_keyword

        self.__keyed_values_nb = 0
        self.__keys = []
        self.__keys_length = 1

        self.set_gbkf_version()
        self.set_specification_id()
        self.set_specification_version()
        self.set_keys_length()
        self.set_keyed_values_nb()

    def set_gbkf_version(self, uint1:int = 0):
        self.__set_integer(uint1,
                           min_value=0,
                           max_value=Constants._uint_8_max,
                           start_pos=Constants.Header._gbkf_version_start,
                           length=Constants.Header._gbkf_version_length)


    def set_specification_id(self, uint3:int = 0):
        self.__set_integer(uint3,
                           min_value=0,
                           max_value=Constants._uint_32_max,
                           start_pos=Constants.Header._specification_id_start,
                           length=Constants.Header._specification_id_length)

    def set_specification_version(self, uint_2:int = 0):
        self.__set_integer(uint_2,
                           min_value=0,
                           max_value=Constants._uint_16_max,
                           start_pos=Constants.Header._specification_version_start,
                           length=Constants.Header._specification_version_length)

    def set_keys_length(self, uint1:int = 1):

        if any(len(key) != uint1 for key in self.__keys):
            raise ValueError(f"Impossible to set keys length={uint1}, since there are already keys with another length.")

        self.__set_integer(uint1,
                           min_value=1,
                           max_value=Constants._uint_8_max,
                           start_pos=Constants.Header._keys_length_start,
                           length=Constants.Header._keys_length_length)

        self.__keys_length = uint1

    def set_keyed_values_nb(self, uint3:int = 0):
        self.__set_integer(uint3,
                           min_value=0,
                           max_value=Constants._uint_32_max,
                           start_pos=Constants.Header._keyed_values_nb_start,
                           length=Constants.Header._keyed_values_nb_length)

    def set_keyed_values_nb_auto(self):
        self.set_keyed_values_nb(self.__keyed_values_nb)

    def add_line_integers(self, key:str, instance_id:int, integers:Sequence[int]):

        values_nb = len(integers)

        # Set the header
        line_bytes = self.__get_keyed_values_header(key=key,
                                                    instance_id=instance_id,
                                                    values_nb=values_nb,
                                                    values_type=Constants.KeyedValues.Types._integer)

        # Set the integers length
        if values_nb == 0:
            values_length = 1
        else:
            values_length = get_uint_length(max(integers))

        line_bytes += self.__format_integer(values_length,
                                            Constants.KeyedValues._integers_length_length)

        # Set the values
        for integer in integers:
            line_bytes += self.__format_integer(integer, values_length)

        # Add to the buffer
        self.__byte_buffer += line_bytes
        self.__keyed_values_nb += 1

        if key not in self.__keys:
            self.__keys.append(key)

    def add_line_single(self, key:str, instance_id:int, singles:Sequence[float]):

        line_bytes = self.__get_keyed_values_header(key=key,
                                                    instance_id=instance_id,
                                                    values_nb=len(singles),
                                                    values_type=Constants.KeyedValues.Types._single)

        for single in singles:
            line_bytes += self.__format_single(single)

        self.__byte_buffer += line_bytes
        self.__keyed_values_nb += 1

        if key not in self.__keys:
            self.__keys.append(key)

    def add_line_double(self, key:str, instance_id:int, doubles:Sequence[float]):

        line_bytes = self.__get_keyed_values_header(key=key,
                                                    instance_id=instance_id,
                                                    values_nb=len(doubles),
                                                    values_type=Constants.KeyedValues.Types._double)

        for double in doubles:
            line_bytes += self.__format_double(double)

        self.__byte_buffer += line_bytes
        self.__keyed_values_nb += 1

        if key not in self.__keys:
            self.__keys.append(key)

    def write(self, write_path:str, auto:bool=True):

        if auto:
            self.set_keyed_values_nb_auto()

        sanity_hash = sha256(self.__byte_buffer).digest()

        with open(write_path, "wb") as f:
            f.write(self.__byte_buffer + sanity_hash)

    def __format_key(self, key:str):

        if key == "":
            raise ValueError("Key cannot be empty.")

        elif len(key) != self.__keys_length:
            raise ValueError(f"The key={key} does not match the keys length={self.__keys_length}")

        return key.encode('ascii')

    @staticmethod
    def __format_integer(value:int, length:int):

        if value < 0:
            raise ValueError("Integer cannot be negative")

        max_value = get_uint_max(length)

        if value > max_value:
            raise ValueError(f"Integer {value} > {max_value}")

        binary_data = value.to_bytes(length, byteorder='big', signed=False)
        return binary_data

    @staticmethod
    def __format_single(value:float):

        # if value < 0:
        #     raise ValueError("Integer cannot be negative")
        #
        if value > Constants._single_max: # Todo  why this is not working?
            raise ValueError(f"Single {value} > {Constants._single_max}")

        return struct.pack('>f', value)

    @staticmethod
    def __format_double(value:float):

        # if value < 0:
        #     raise ValueError("Integer cannot be negative")
        #
        if value > Constants._double_max: # Todo  why this is not working?
            raise ValueError(f"Double {value} > {Constants._double_max}")

        return struct.pack('>d', value)

    def __set_integer(self,
                      value:int,
                      min_value:int,
                      max_value:int,
                      start_pos:int,
                      length: int):
        verify_int(value, min_value=min_value, max_value=max_value)
        binary_value = value.to_bytes(length, byteorder='big', signed=False)
        self.__byte_buffer[start_pos:start_pos+length] = binary_value

    def __get_keyed_values_header(self,
                                  key:str,
                                  instance_id:int,
                                  values_nb:int,
                                  values_type:int) -> bytearray:

        if values_type not in Constants.KeyedValues.Types._all:
            raise ValueError(f"Un-valid KeyedValues.Type={values_type}")

        line_bytes = bytearray()
        line_bytes += self.__format_key(key)
        line_bytes += self.__format_integer(instance_id, Constants.KeyedValues._instance_id_length)
        line_bytes += self.__format_integer(values_nb, Constants.KeyedValues._values_nb_length)
        line_bytes += self.__format_integer(values_type, Constants.KeyedValues._values_type_length)

        return line_bytes