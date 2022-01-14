# Copyright 2022 AccelByte Inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for `justice_common_log.utils` module."""

import unittest

from justice_python_common_log.utils import decodeToken, getRequestBody, getResponseBody, minifyJsonString, isSupportedContentType
from tests.data.dummy import TEST_CONTENT_TYPE, TEST_TOKEN, TEST_LARGE_DATA, TEST_RESPONSE_BODY, TEST_RESPONSE_BODY_RESULT, TEST_REQUEST_BODY, TEST_REQUEST_BODY_RESULT, TEST_INVALID_CONTENT_TYPE


class TestUtils(unittest.TestCase):
    """Tests for `justice_common_log` package."""

    def test_get_request_body(self):
        result = getRequestBody(TEST_REQUEST_BODY, TEST_CONTENT_TYPE)
        self.assertEqual(result, TEST_REQUEST_BODY_RESULT)

    def test_get_request_body_too_large(self):
        result = getRequestBody(TEST_LARGE_DATA, TEST_CONTENT_TYPE)
        self.assertEqual(result, 'data too large')

    def test_get_request_invalid_content_type(self):
        result = getRequestBody(TEST_REQUEST_BODY, TEST_INVALID_CONTENT_TYPE)
        self.assertEqual(result, '')

    def test_get_response_body(self):
        result = getResponseBody(TEST_RESPONSE_BODY, TEST_CONTENT_TYPE)
        self.assertEqual(result, TEST_RESPONSE_BODY_RESULT)

    def test_get_response_body_too_large(self):
        result = getResponseBody(TEST_LARGE_DATA, TEST_CONTENT_TYPE)
        self.assertEqual(result, 'data too large')

    def test_get_response_invalid_content_type(self):
        result = getResponseBody(TEST_RESPONSE_BODY, TEST_INVALID_CONTENT_TYPE)
        self.assertEqual(result, '')

    def test_minify_json_string(self):
        result = minifyJsonString(TEST_REQUEST_BODY)
        self.assertEqual(result, TEST_REQUEST_BODY_RESULT)

    def test_is_support_content_type(self):
        result = isSupportedContentType(TEST_CONTENT_TYPE)
        self.assertEqual(result, True)

    def test_is_support_content_type_invalid(self):
        result = isSupportedContentType(TEST_INVALID_CONTENT_TYPE)
        self.assertEqual(result, False)
        
    def test_decode_token(self):
        result = decodeToken(TEST_TOKEN)
        assert 'namespace' in result

