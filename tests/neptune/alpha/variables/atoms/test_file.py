#
# Copyright (c) 2020, Neptune Labs Sp. z o.o.
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

# pylint: disable=protected-access
import os

from mock import MagicMock

from neptune.alpha.internal.operation import UploadFile
from neptune.alpha.variables.atoms.file import File, FileVal

from tests.neptune.alpha.variables.test_variable_base import TestVariableBase


class TestFile(TestVariableBase):

    def test_assign(self):
        value_and_expected = [
            ("some/path", os.getcwd() + "/some/path"),
            (FileVal("other/../other/file.txt"), os.getcwd() + "/other/file.txt")
        ]

        for value, expected in value_and_expected:
            backend, processor = MagicMock(), MagicMock()
            exp, path, wait = self._create_experiment(backend, processor), self._random_path(), self._random_wait()
            var = File(exp, path)
            var.assign(value, wait=wait)
            processor.enqueue_operation.assert_called_once_with(UploadFile(path, expected), wait)

    def test_assign_type_error(self):
        values = [55, None, []]
        for value in values:
            with self.assertRaises(TypeError):
                File(MagicMock(), MagicMock()).assign(value)

    def test_save(self):
        value_and_expected = [
            ("some/path", os.getcwd() + "/some/path")
        ]

        for value, expected in value_and_expected:
            backend, processor = MagicMock(), MagicMock()
            exp, path, wait = self._create_experiment(backend, processor), self._random_path(), self._random_wait()
            var = File(exp, path)
            var.save(value, wait=wait)
            processor.enqueue_operation.assert_called_once_with(UploadFile(path, expected), wait)

    def test_save_type_error(self):
        values = [55, None, [], FileVal]
        for value in values:
            with self.assertRaises(TypeError):
                File(MagicMock(), MagicMock()).save(value)