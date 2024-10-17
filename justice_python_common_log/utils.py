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

"""utils module."""

import os
import jwt
import orjson
from .constant import FULL_ACCESS_LOG_SUPPORTED_CONTENT_TYPES, FULL_ACCESS_LOG_MAX_BODY_SIZE

full_access_log_max_body_size = int(os.getenv("FULL_ACCESS_LOG_MAX_BODY_SIZE", FULL_ACCESS_LOG_MAX_BODY_SIZE))
supported_content_type_list = str(os.getenv("FULL_ACCESS_LOG_SUPPORTED_CONTENT_TYPES", FULL_ACCESS_LOG_SUPPORTED_CONTENT_TYPES)).split(",")


def get_request_body(request_context, content_type):
    if not content_type or not is_supported_content_type(content_type):
        return ""

    if len(request_context) != 0:
        if len(request_context) > full_access_log_max_body_size:
            return "data too large"

        if content_type == 'application/json':
            return minify_json_string(request_context)

    return str(request_context)


def get_response_body(response_context, content_type, is_fastapi=False):
    if not content_type or not is_supported_content_type(content_type):
        return ""

    if len(response_context) != 0:
        if len(response_context) > full_access_log_max_body_size:
            return "data too large"

        if is_fastapi:
            return minify_json_string(response_context[0])
        else:
            return minify_json_string(response_context)

    return str(response_context)


def minify_json_string(string_context):
    string_context_compress = orjson.dumps(orjson.loads(string_context)).decode("utf-8")

    return string_context_compress


def is_supported_content_type(content_type):
    if content_type in supported_content_type_list:
        return True

    return False


def decode_token(token):
    try:
        data_token = jwt.decode(token.replace("Bearer ", ""), options={"verify_signature": False})
    except:
        data_token = dict()

    return data_token
