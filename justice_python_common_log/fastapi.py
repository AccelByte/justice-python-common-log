# Copyright 2024 AccelByte Inc
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

"""FastAPI module."""

import logging
import os
import re
import uuid
from datetime import datetime, timezone
from distutils.util import strtobool

from fastapi import FastAPI, Request
from starlette.concurrency import iterate_in_threadpool
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import Message

from .constant import DEFAULT_LOG_FORMAT, FULL_LOG_FORMAT, FULL_ACCESS_LOG_ENABLED, FULL_ACCESS_LOG_MAX_BODY_SIZE
from .utils import get_request_body, decode_token, get_response_body

full_access_log_max_body_size = int(os.getenv("FULL_ACCESS_LOG_MAX_BODY_SIZE", FULL_ACCESS_LOG_MAX_BODY_SIZE))

# configure logger format
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger('justice-common-log')


class LogMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: FastAPI,
        excluded_paths=None,
        excluded_agents=None
    ) -> None:
        super().__init__(app)
        self.excluded_paths = excluded_paths
        self.excluded_agents = excluded_agents

        if self.excluded_paths is not None:
            self.excluded_paths = [re.compile(pattern) for pattern in self.excluded_paths]

        if self.excluded_agents is not None:
            self.excluded_agents = [re.compile(pattern) for pattern in excluded_agents]

    async def dispatch(self, request: Request, call_next):
        if self.should_skip_logging(request):
            return await call_next(request)

        start_time = datetime.now()
        request_body = b''

        # Only read request body if we need it for logging
        if strtobool(os.getenv("FULL_ACCESS_LOG_ENABLED", FULL_ACCESS_LOG_ENABLED)):
            try:
                await set_body(request)
                request_body = await request.body()
            except Exception as e:
                logger.warning(f"Error reading request body: {e}")

        response = await call_next(request)
        process_time = (datetime.now() - start_time).total_seconds() * 1000

        data = {
            "time": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration": int(process_time)
        }

        if strtobool(os.getenv("FULL_ACCESS_LOG_ENABLED", FULL_ACCESS_LOG_ENABLED)):
            try:
                # Headers and token data updates remain the same...

                # Request body processing - only if we have it
                if request_body:
                    data.update({
                        "request_content_type": request.headers.get("Content-Type"),
                        "request_body": get_request_body(request_body, request.headers.get("Content-Type"))
                    })

                # Response body processing - single pass, tracking size
                response_body = []
                total_size = 0
                async for chunk in response.body_iterator:
                    response_body.append(chunk)
                    total_size += len(chunk)

                # Update response data and restore iterator
                if response_body:
                    data.update({
                        "length": total_size,
                        "response_content_type": response.headers.get('content-type'),
                        "response_body": get_response_body(b''.join(response_body),
                                                           response.headers.get('content-type'),
                                                           is_fastapi=True)
                    })

                response.body_iterator = iterate_in_threadpool(iter(response_body))

                # Log using full format
                logger.info(FULL_LOG_FORMAT.format(
                    data.get("time"),
                    data.get("method"),
                    data.get("path"),
                    data.get("status"),
                    data.get("duration"),
                    data.get("length", 0),
                    data.get("user_ip", ""),
                    data.get("user_agent", ""),
                    data.get("referer", ""),
                    data.get("trace_id", ""),
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
            except Exception as e:
                logger.error(f"Error in full logging: {e}")
                # Fallback to default logging
                logger.info(DEFAULT_LOG_FORMAT.format(
                    data.get("time"),
                    data.get("method"),
                    data.get("path"),
                    data.get("status"),
                    data.get("duration")
                ))
        else:
            logger.info(DEFAULT_LOG_FORMAT.format(
                data.get("time"),
                data.get("method"),
                data.get("path"),
                data.get("status"),
                data.get("duration")
            ))

        return response


    def should_skip_logging(self, request: Request) -> bool:
        """Check if logging should be skipped"""
        if self.excluded_agents and request.headers.get("User-Agent"):
            if any(pattern.match(request.headers.get("User-Agent")) for pattern in self.excluded_agents):
                return True

        if self.excluded_paths:
            if any(pattern.fullmatch(request.url.path) for pattern in self.excluded_paths):
                return True

        return False

async def set_body(request: Request):
    receive_ = await request._receive()

    async def receive() -> Message:
        return receive_

    request._receive = receive

class Log:
    """Log FastAPI extensions class."""

    def __init__(self, app: FastAPI = None, excluded_paths=None, excluded_agents=None) -> None:
        self.app = app
        self.excluded_paths = excluded_paths
        self.excluded_agents = excluded_agents

        if app is not None:
            self.init_app(app)

    def init_app(self, app: FastAPI):
        app.add_middleware(LogMiddleware, excluded_paths=self.excluded_paths, excluded_agents=self.excluded_agents)
