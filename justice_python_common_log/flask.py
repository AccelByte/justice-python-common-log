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

"""Flask module."""

import os
import re
import uuid
import logging
from distutils.util import strtobool
from datetime import datetime, timezone
from flask import g, Flask, request
from flask.wrappers import Response
from .constant import DEFAULT_LOG_FORMAT, FULL_LOG_FORMAT, FULL_ACCESS_LOG_ENABLED
from .utils import getRequestBody, getResponseBody, decodeToken

# configure logger format
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger('justice-common-log')


class Log:
    """Log Flask extensions class.
    """

    def __init__(self, app: Flask = None, excluded_paths=None, excluded_agents=None) -> None:
        self.app = app
        self.app = app
        self.excluded_paths = excluded_paths
        self.excluded_agents = excluded_agents
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.disabled = True

        if self.excluded_paths is not None:
            self.excluded_paths = [re.compile(pattern) for pattern in self.excluded_paths]

        if self.excluded_agents is not None:
            self.excluded_agents = [re.compile(pattern) for pattern in excluded_agents]

        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask):
        app.before_request(self.start_request_time)
        app.after_request(self.filter)

    def start_request_time(self):
        g.start = datetime.now()

    def filter(self, response: Response) -> Response:

        response.direct_passthrough = False

        if self.excluded_agents:
            if request.headers.get("User-Agent") is not None:
                if any(pattern.match(request.headers.get("User-Agent")) for pattern in self.excluded_agents):
                    return response

        if self.excluded_paths:
            if any(pattern.fullmatch(request.path) for pattern in self.excluded_paths):
                return response

        data = {
            "time": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "realm": os.getenv("REALM", "dev"),
            "method": request.method,
            "path": request.path,
            "status": response.status_code,
            "duration": int((datetime.now() - g.start).total_seconds() * 1000)
        }

        if strtobool(os.getenv("FULL_ACCESS_LOG_ENABLED", FULL_ACCESS_LOG_ENABLED)):

            data["user_agent"] = request.headers.get("User-Agent", "")
            data["referer"] = request.headers.get("Referer", "")
            data["user_ip"] = request.headers.get("X-Forwarded-For", request.remote_addr)
            data["trace_id"] = request.headers.get("X-Ab-TraceID", uuid.uuid4().hex)
            data["flight_id"] = request.headers.get("x-flight-id", "")
            data["game_version"] = request.headers.get("Game-Client-Version", "")
            data["sdk_version"] = request.headers.get("AccelByte-SDK-Version", "")
            data["oss_version"] = request.headers.get("AccelByte-OSS-Version", "")

            if request.headers.get("Authorization"):
                data_token = decodeToken(request.headers.get("Authorization"))
                data["user_id"] = data_token.get("user_id", "")
                data["client_id"] = data_token.get("client_id", "")
                data["namespace"] = data_token.get("namespace", "")

            if request.data:
                data["request_content_type"] = request.content_type
                data["request_body"] = getRequestBody(request.data, request.content_type)

            if response.data:
                data["length"] = len(response.data)
                data["response_content_type"] = response.content_type
                data["response_body"] = getResponseBody(response.data, response.content_type)

            logger.info(FULL_LOG_FORMAT.format(
                data.get("time"),
                data.get("method"),
                data.get("path"),
                data.get("status"),
                data.get("duration"),
                data.get("length", 0),
                data.get("user_ip"),
                data.get("user_agent"),
                data.get("referer"),
                data.get("trace_id"),
                data.get("namespace", ""),
                data.get("user_id", ""),
                data.get("client_id", ""),
                data.get("request_content_type", ""),
                data.get("request_body", ""),
                data.get("response_content_type", ""),
                data.get("response_body", ""),
                data.get("flight_id", ""),
                data.get("game_version", ""),
                data.get("sdk_version", ""),
                data.get("oss_version", "")
            ))

        else:

            logger.info(DEFAULT_LOG_FORMAT.format(
                data.get("time"),
                data.get("realm"),
                data.get("method"),
                data.get("path"),
                data.get("status"),
                data.get("duration")
            ))

        return response
