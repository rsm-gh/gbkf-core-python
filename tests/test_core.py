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

import os
import sys
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

import GBKFCore
from GBKFCoreReader import GBKFCoreReader
from GBKFCoreWriter import GBKFCoreWriter


class TestGBKFCore(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._work_dir = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._work_dir)

    def test_header(self):

        test_data = (
            # gbkf_version   specification_id       specification_version    keys_size            keyed_values_nb
            (0, 0, 0, 1, 1),  # Min
            (GBKFCore.ValueTypeBoundaries._uint_8_max, GBKFCore.ValueTypeBoundaries._uint_32_max, GBKFCore.ValueTypeBoundaries._uint_16_max,
             GBKFCore.ValueTypeBoundaries._uint_8_max, GBKFCore.ValueTypeBoundaries._uint_32_max),  # Max
            (10, 11, 12, 13, 13),  # Value
        )

        for test_index, (gbkf_version,
                         specification_id,
                         specification_version,
                         keys_size,
                         keyed_values_nb) in enumerate(test_data):
            test_path = os.path.join(self._work_dir, f"test_core_header_{test_index}.gbkf")

            #
            # Write the data
            #
            gbkf_writer = GBKFCoreWriter()
            gbkf_writer.set_gbkf_version(gbkf_version)
            gbkf_writer.set_specification_id(specification_id)
            gbkf_writer.set_specification_version(specification_version)
            gbkf_writer.set_keys_size(keys_size)
            gbkf_writer.set_keyed_values_nb(keyed_values_nb)

            gbkf_writer.write(test_path, auto_update=False, add_footer= test_index>1)

            #
            # Read the data & test
            #
            gbkf_reader = GBKFCoreReader(test_path)
            self.assertEqual(gbkf_reader.get_gbkf_version(), gbkf_version)
            self.assertEqual(gbkf_reader.get_specification_id(), specification_id)
            self.assertEqual(gbkf_reader.get_specification_version(), specification_version)
            self.assertEqual(gbkf_reader.get_keys_size(), keys_size)
            self.assertEqual(gbkf_reader.get_keyed_values_nb(), keyed_values_nb)
            self.assertEqual(gbkf_reader.verifies_sha(), test_index>1)

    def test_values(self):

        test_path = os.path.join(self._work_dir, "test_core_values.gbkf")

        input_values_uint8 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 255]
        input_values_uint16 = [1, 200, 300, 400, 45, 600, 700, 800, 900, 1000]
        input_values_uint32 = [100, 200, 1, 400, 500, 600, 700, 454545, 900, 1000]
        input_values_uint64 = [100, 454545, 300, 400, 500, 600, 1, 800, 900, 1000]

        input_values_int8 = [-1, 2, 3, 4, -5, 6, 7, 8, 9, 10, 100]
        input_values_int16 = [1, 200, -300, 400, 45, -600, 700, 800, 900, 1000]
        input_values_int32 = [100, 200, 1, 400, 500, -600, 700, 454545, -900, 1000]
        input_values_int64 = [100, -454545, 300, 400, 500, 600, 1, 800, -900, 1000]

        #input_booleans = [True, True, True, True, False, False, False, False, True, False]
        input_floats32 = [0, .3467846785, 6.5, 110.9, -15000.865]
        input_floats64 = [0, .3434546785, 1.5, 1000.9, -10000.865]
        #input_blobs = [0b11001100, 0b10101010, 0b11110000]

        #
        # Write the data
        #
        gbkf_writer = GBKFCoreWriter()
        gbkf_writer.set_keys_size(2)

        gbkf_writer.add_keyed_values_uint8(key="UI",
                                           instance_id=1,
                                           integers=input_values_uint8)

        gbkf_writer.add_keyed_values_uint16(key="UI",
                                            instance_id=2,
                                            integers=input_values_uint16)

        gbkf_writer.add_keyed_values_uint32(key="UI",
                                            instance_id=3,
                                            integers=input_values_uint32)

        gbkf_writer.add_keyed_values_uint64(key="UI",
                                            instance_id=4,
                                            integers=input_values_uint64)

        gbkf_writer.add_keyed_values_int8(key="SI",
                                           instance_id=1,
                                           integers=input_values_int8)

        gbkf_writer.add_keyed_values_int16(key="SI",
                                            instance_id=2,
                                            integers=input_values_int16)

        gbkf_writer.add_keyed_values_int32(key="SI",
                                            instance_id=3,
                                            integers=input_values_int32)

        gbkf_writer.add_keyed_values_int64(key="SI",
                                            instance_id=4,
                                            integers=input_values_int64)


        gbkf_writer.add_keyed_values_float32(key="F3",
                                             instance_id=5,
                                             singles=input_floats32)

        gbkf_writer.add_keyed_values_float64(key="F6",
                                             instance_id=1,
                                             doubles=input_floats64)

        gbkf_writer.write(test_path, auto_update=True)

        #
        # Read the data
        #

        gbkf_reader = GBKFCoreReader(test_path)
        keyed_values = gbkf_reader.get_keyed_values()

        output_entry_uint8 = keyed_values["UI"][0]
        self.assertEqual(output_entry_uint8.get_type(), GBKFCore.ValueType.UINT8)
        self.assertEqual(output_entry_uint8.instance_id, 1)
        self.assertEqual(output_entry_uint8.get_values(), input_values_uint8)

        output_entry_uint16 = keyed_values["UI"][1]
        self.assertEqual(output_entry_uint16.get_type(), GBKFCore.ValueType.UINT16)
        self.assertEqual(output_entry_uint16.instance_id, 2)
        self.assertEqual(output_entry_uint16.get_values(), input_values_uint16)

        output_entry_uint32 = keyed_values["UI"][2]
        self.assertEqual(output_entry_uint32.get_type(), GBKFCore.ValueType.UINT32)
        self.assertEqual(output_entry_uint32.instance_id, 3)
        self.assertEqual(output_entry_uint32.get_values(), input_values_uint32)

        output_entry_uint64 = keyed_values["UI"][3]
        self.assertEqual(output_entry_uint64.get_type(), GBKFCore.ValueType.UINT64)
        self.assertEqual(output_entry_uint64.instance_id, 4)
        self.assertEqual(output_entry_uint64.get_values(), input_values_uint64)

        output_entry_int8 = keyed_values["SI"][0]
        self.assertEqual(output_entry_int8.get_type(), GBKFCore.ValueType.INT8)
        self.assertEqual(output_entry_int8.instance_id, 1)
        self.assertEqual(output_entry_int8.get_values(), input_values_int8)

        output_entry_int16 = keyed_values["SI"][1]
        self.assertEqual(output_entry_int16.get_type(), GBKFCore.ValueType.INT16)
        self.assertEqual(output_entry_int16.instance_id, 2)
        self.assertEqual(output_entry_int16.get_values(), input_values_int16)

        output_entry_int32 = keyed_values["SI"][2]
        self.assertEqual(output_entry_int32.get_type(), GBKFCore.ValueType.INT32)
        self.assertEqual(output_entry_int32.instance_id, 3)
        self.assertEqual(output_entry_int32.get_values(), input_values_int32)

        output_entry_int64 = keyed_values["SI"][3]
        self.assertEqual(output_entry_int64.get_type(), GBKFCore.ValueType.INT64)
        self.assertEqual(output_entry_int64.instance_id, 4)
        self.assertEqual(output_entry_int64.get_values(), input_values_int64)


        output_entry_float32 = keyed_values["F3"][0]
        self.assertEqual(output_entry_float32.get_type(), GBKFCore.ValueType.FLOAT32)
        self.assertEqual(output_entry_float32.instance_id, 5)
        output_entry_float32_values = output_entry_float32.get_values()
        for i, input_value in enumerate(input_floats32):
            self.assertAlmostEqual(output_entry_float32_values[i], input_value, delta=1e-3)

        output_entry_float64 = keyed_values["F6"][0]
        self.assertEqual(output_entry_float64.get_type(), GBKFCore.ValueType.FLOAT64)
        self.assertEqual(output_entry_float64.instance_id, 1)
        output_entry_float64_values = output_entry_float64.get_values()
        for i, input_value in enumerate(input_floats64):
            self.assertAlmostEqual(output_entry_float64_values[i], input_value, delta=1e-3)

        self.assertTrue(gbkf_reader.verifies_sha())


if __name__ == '__main__':
    unittest.main()
