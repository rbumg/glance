# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright 2010-2011 OpenStack, LLC
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import commands
import datetime
import os
import re

from glance.common import crypt
from glance.common import utils
from glance.openstack.common import importutils
from glance.tests import utils as test_utils


class UtilsTestCase(test_utils.BaseTestCase):

    def test_bool_from_string(self):
        true_values = ['True', True, 'true', 'TRUE', '1', 1, 'on',
                       'ON', 'y', 'yes', 'Y', 'YES']

        i = 0
        for value in true_values:
            self.assertTrue(utils.bool_from_string(value),
                            "Got False for value: %r (%d)" % (value, i))
            i = i + 1

        false_values = ['False', False, 'false', 'T', 'F', 'FALSE',
                        '0', 0, 9, 'off', 'OFF', 'no', 'n', 'NO', 'N']

        for value in false_values:
            self.assertFalse(utils.bool_from_string(value),
                             "Got True for value: %r" % value)

    def test_encryption(self):
        # Check that original plaintext and unencrypted ciphertext match
        # Check keys of the three allowed lengths
        key_list = ["1234567890abcdef",
                    "12345678901234567890abcd",
                    "1234567890abcdef1234567890ABCDEF"]
        plaintext_list = ['']
        blocksize = 64
        for i in range(3 * blocksize):
            plaintext_list.append(os.urandom(i))

        for key in key_list:
            for plaintext in plaintext_list:
                ciphertext = crypt.urlsafe_encrypt(key, plaintext, blocksize)
                self.assertTrue(ciphertext != plaintext)
                text = crypt.urlsafe_decrypt(key, ciphertext)
                self.assertTrue(plaintext == text)

    def test_empty_metadata_headers(self):
        """Ensure unset metadata is not encoded in HTTP headers"""

        metadata = {
            'foo': 'bar',
            'snafu': None,
            'bells': 'whistles',
            'unset': None,
            'empty': '',
            'properties': {
                'distro': '',
                'arch': None,
                'user': 'nobody',
            },
        }

        headers = utils.image_meta_to_http_headers(metadata)

        self.assertFalse('x-image-meta-snafu' in headers)
        self.assertFalse('x-image-meta-uset' in headers)
        self.assertFalse('x-image-meta-snafu' in headers)
        self.assertFalse('x-image-meta-property-arch' in headers)

        self.assertEquals(headers.get('x-image-meta-foo'), 'bar')
        self.assertEquals(headers.get('x-image-meta-bells'), 'whistles')
        self.assertEquals(headers.get('x-image-meta-empty'), '')
        self.assertEquals(headers.get('x-image-meta-property-distro'), '')
        self.assertEquals(headers.get('x-image-meta-property-user'), 'nobody')
