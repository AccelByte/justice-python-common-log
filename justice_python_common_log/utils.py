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


fullAccessLogMaxBodySize = int(os.getenv("FULL_ACCESS_LOG_MAX_BODY_SIZE", FULL_ACCESS_LOG_MAX_BODY_SIZE))
supportedContentTypeList = str(os.getenv("FULL_ACCESS_LOG_SUPPORTED_CONTENT_TYPES", FULL_ACCESS_LOG_SUPPORTED_CONTENT_TYPES)).split(",")

def getRequestBody(requestContext, contentType):

    if not contentType or not isSupportedContentType(contentType):
        return ""

    if len(requestContext) != 0:
        if len(requestContext) > fullAccessLogMaxBodySize:
            return "data too large"

        if contentType == 'application/json':
            return minifyJsonString(requestContext)

    return str(requestContext)
    

def getResponseBody(responseContext, contentType):

    if not contentType or not isSupportedContentType(contentType):
        return ""

    if len(responseContext) != 0:
        if len(responseContext) > fullAccessLogMaxBodySize:
            return "data too large"

        if contentType == 'application/json':
            return minifyJsonString(responseContext)

    return str(responseContext)


def minifyJsonString(stringContext):

    stringContextCompress = orjson.dumps(orjson.loads(stringContext)).decode("utf-8")

    return stringContextCompress


def isSupportedContentType(contentType):

    if contentType in supportedContentTypeList:
        return True
    
    return False


def decodeToken(token):

    try:
        data_token = jwt.decode(token.replace("Bearer ", ""), options={"verify_signature": False})
    except:
        data_token = dict()

    return data_token