#
# Copyright (c) 2021, Neptune Labs Sp. z o.o.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import time
import unittest
from typing import List

import mock
from freezegun import freeze_time
from mock import MagicMock

from neptune.internal.backends.alpha_integration_backend import AlphaIntegrationBackend
from neptune.internal.channels.channels import ChannelIdWithValues, ChannelValue
from tests.neptune.alpha.backend_test_mixin import BackendTestMixin as AlphaBackendTestMixin

API_TOKEN = 'eyJhcGlfYWRkcmVzcyI6Imh0dHBzOi8vYWxwaGEuc3RhZ2UubmVwdHVuZS5haSIsImFwaV91cmwiOiJodHRwczovL2FscG' \
            'hhLnN0YWdlLm5lcHR1bmUuYWkiLCJhcGlfa2V5IjoiZDg5MGQ3Y2ItZGEzNi00MjRkLWJhNTQtZmVjZDJmYTdhOTQzIn0='
"""base64 decoded `API_TOKEN`
{
  "api_address": "https://alpha.stage.neptune.ai",
  "api_url": "https://alpha.stage.neptune.ai",
  "api_key": "d890d7cb-da36-424d-ba54-fecd2fa7a943"
}
"""


class TestAlphaIntegrationNeptuneBackend(unittest.TestCase, AlphaBackendTestMixin):
    @mock.patch('bravado.client.SwaggerClient.from_url')
    @mock.patch('neptune.internal.backends.hosted_neptune_backend.NeptuneAuthenticator', new=MagicMock)
    @mock.patch('neptune.alpha.internal.backends.hosted_neptune_backend.NeptuneAuthenticator', new=MagicMock)
    def setUp(self, swagger_client_factory) -> None:
        # pylint:disable=arguments-differ
        self._get_swagger_client_mock(swagger_client_factory)
        self.backend = AlphaIntegrationBackend(API_TOKEN)
        self.exp_mock = MagicMock(
            internal_id='00000000-0000-0000-0000-000000000000'
        )

    @freeze_time()
    def _test_send_channel_values(self, channel_y_elements: List[tuple], expected_operation: str):
        # given prepared `ChannelIdWithValues`
        channel_id = 'channel_id'
        now_ms = int(time.time() * 1000)
        channel_with_values = ChannelIdWithValues(
            channel_id=channel_id,
            channel_values=[
                ChannelValue(x=None, y={channel_y_key: channel_y_value}, ts=None)
                for channel_y_key, channel_y_value in channel_y_elements
            ]
        )

        # invoke send_channels_values
        self.backend.send_channels_values(self.exp_mock, [channel_with_values])

        # expect `executeOperations` was called once with properly prepared kwargs
        expected_call_args = {
            'experimentId': '00000000-0000-0000-0000-000000000000',
            'operations': [{
                'path': channel_id,
                expected_operation: {
                    'entries': [
                        {'value': channel_y_value, 'step': None, 'timestampMilliseconds': now_ms}
                        for _, channel_y_value in channel_y_elements
                    ]
                }
            }]
        }
        # pylint:disable=protected-access
        execute_operations = self.backend._alpha_backend.leaderboard_client.api.executeOperations
        self.assertEqual(len(execute_operations.call_args_list), 1)
        self.assertDictEqual(execute_operations.call_args_list[0][1], expected_call_args)

    def test_send_channels_text_values(self):
        channel_y_elements = [
            ('text_value', 'Line of text'),
            ('text_value', 'Another line of text'),
        ]
        self._test_send_channel_values(channel_y_elements, expected_operation='logStrings')

    def test_send_channels_numeric_values(self):
        channel_y_elements = [
            ('numeric_value', 42),
            ('numeric_value', 0.07),
        ]
        self._test_send_channel_values(channel_y_elements, expected_operation='logFloats')

    def test_send_channels_image_values(self):
        """TODO: implement in NPT-9207"""