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
import unittest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src"))

from GBKFCore import Constants, Reader, Writer

class TestGBKFCore(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls._work_dir = tempfile.mkdtemp()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls._work_dir)

    def test_header(self):

        test_data = (
            #gbkf_version           specification_id       specification_version    keys_length            keyed_values_nb
            (0,                     0,                     0,                       1,                     1                    ), # Min
            (Constants._uint_8_max, Constants._uint_32_max, Constants._uint_16_max, Constants._uint_8_max, Constants._uint_32_max), # Max
            (10,                    11,                    12,                      13,                    13                   ), # Value
        )

        for test_index, (gbkf_version, specification_id, specification_version, keys_length, keyed_values_nb) in enumerate(test_data):

            test_path = os.path.join(self._work_dir, f"test_core_header_{test_index}.gbkf")

            #
            # Write the data
            #
            gbkf_writer = Writer()
            gbkf_writer.set_gbkf_version(gbkf_version)
            gbkf_writer.set_specification_id(specification_id)
            gbkf_writer.set_specification_version(specification_version)
            gbkf_writer.set_keys_length(keys_length)
            gbkf_writer.set_keyed_values_nb(keyed_values_nb)

            gbkf_writer.write(test_path, auto=False)

            #
            # Read the data & test
            #
            gbkf_reader = Reader(test_path)
            self.assertEqual(gbkf_reader.get_gbkf_version(), gbkf_version)
            self.assertEqual(gbkf_reader.get_specification_id(), specification_id)
            self.assertEqual(gbkf_reader.get_specification_version(), specification_version)
            self.assertEqual(gbkf_reader.get_keys_length(), keys_length)
            self.assertEqual(gbkf_reader.get_keyed_values_nb(), keyed_values_nb)
            self.assertTrue(gbkf_reader.verifies_sha())


    def test_values(self):

        test_path = os.path.join(self._work_dir, "test_core_values.gbkf")

        integer_pos_key = "IP"

        integer_pos1_instance_id = 1
        integer_pos1_values = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

        integer_pos2_instance_id = 2
        integer_pos2_values = (100, 200, 300, 400, 500, 600, 700, 800, 900, 1000)

        single_key = "SS"
        single_1_instance_id = 1
        single_1_values = (0, .6575, 1.5, 100.9, -10.864)

        double_key = "DD"
        double_1_instance_id = 1
        double_1_values = (0, .3434546785, 1.5, 1000.9, -10000.865)

        #
        # Write the data
        #
        gbkf_writer = Writer()
        gbkf_writer.set_keys_length(2)

        gbkf_writer.add_line_integers(key=integer_pos_key,
                                      instance_id=integer_pos1_instance_id,
                                      integers=integer_pos1_values)

        gbkf_writer.add_line_integers(key=integer_pos_key,
                                      instance_id=integer_pos2_instance_id,
                                      integers=integer_pos2_values)

        gbkf_writer.add_line_single(key=single_key,
                                    instance_id=single_1_instance_id,
                                    singles=single_1_values)

        gbkf_writer.add_line_double(key=double_key,
                                    instance_id=double_1_instance_id,
                                    doubles=double_1_values)

        gbkf_writer.write(test_path, auto=True)

        #
        # Read the data
        #

        gbkf_reader = Reader(test_path)
        keyed_values = gbkf_reader.get_keyed_values()

        read_integer_pos1 = keyed_values[integer_pos_key][0]

        self.assertEqual(read_integer_pos1, (integer_pos1_instance_id,
                                                    len(integer_pos1_values),
                                                    Constants.KeyedValues.Types._integer,
                                                    integer_pos1_values))


        read_integer_pos2 = keyed_values[integer_pos_key][1]
        self.assertEqual(read_integer_pos2, (integer_pos2_instance_id,
                                                    len(integer_pos2_values),
                                                    Constants.KeyedValues.Types._integer,
                                                    integer_pos2_values))

        read_singles = keyed_values[single_key][0]
        self.compare_item_values((single_1_instance_id,
                                      len(single_1_values),
                                      Constants.KeyedValues.Types._single,
                                      single_1_values),
                           read_singles)

        read_doubles = keyed_values[double_key][0]
        self.compare_item_values((double_1_instance_id,
                                                len(double_1_values),
                                                Constants.KeyedValues.Types._double,
                                                double_1_values),
                           read_doubles)

        self.assertTrue(gbkf_reader.verifies_sha())


    def compare_item_values(self, base_items, compare_items, accepted_error=1e-4):
        """
            Compare a list of numbers, and the list can contain sub-lists of floats.
            [1, 3, 5, [3.44, 234.56]]
        """

        for item_index, base_item in enumerate(base_items):
            compare_item = compare_items[item_index]

            if isinstance(compare_item, int):
                self.assertEqual(base_item, compare_item)

            else:

                for value_index, base_value in enumerate(base_item):
                    compare_value = compare_item[value_index]
                    self.assertAlmostEqual(base_value, compare_value, delta=accepted_error)


if __name__ == '__main__':
    unittest.main()

