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

from .constant import DEFAULT_LOG_FORMAT, FULL_LOG_FORMAT, FULL_ACCESS_LOG_ENABLED
from .utils import get_request_body, decode_token, get_response_body

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
        start_time = datetime.now()
        response = await call_next(request)
        process_time = (datetime.now() - start_time).total_seconds() * 1000

        if self.excluded_agents:
            if request.headers.get("User-Agent") is not None:
                if any(pattern.match(request.headers.get("User-Agent")) for pattern in self.excluded_agents):
                    return response

        if self.excluded_paths:
            if any(pattern.fullmatch(request.url.path) for pattern in self.excluded_paths):
                return response

        data = {
            "time": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
            "method": request.method,
            "path": request.url.path,
            "status": response.status_code,
            "duration": int(process_time)
        }

        logger.info(DEFAULT_LOG_FORMAT.format(
            data.get("time"),
            data.get("method"),
            data.get("path"),
            data.get("status"),
            data.get("duration")
        ))

        return response

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
