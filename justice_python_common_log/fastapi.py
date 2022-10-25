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

"""Fastapi module."""

import os
import uuid
import re
import logging
from distutils.util import strtobool
from datetime import datetime, timezone
from fastapi import FastAPI, Request
from starlette.concurrency import iterate_in_threadpool
from .constant import DEFAULT_LOG_FORMAT, FULL_LOG_FORMAT, FULL_ACCESS_LOG_ENABLED
from .utils import getRequestBody, getResponseBody, decodeToken
from starlette.types import Message


class Log:
    """Log FastAPI middleware class.
    """

    def __init__(self, app: FastAPI = None, excluded_paths=None, excluded_agents=None) -> None:
        self.app = app
        self.excluded_paths = excluded_paths
        self.excluded_agents = excluded_agents

        # configure root logger
        logging.basicConfig(level=logging.INFO, format='%(message)s')
        log = logging.getLogger('uvicorn.access')
        log.setLevel(logging.ERROR)

        if self.excluded_paths is not None:
            self.excluded_paths = [re.compile(pattern) for pattern in self.excluded_paths]

        if self.excluded_agents is not None:
            self.excluded_agents = [re.compile(pattern) for pattern in excluded_agents]

        if app is not None:
            @app.middleware("http")
            async def filter(request: Request, call_next):

                start_time = datetime.now(timezone.utc)
                await self.set_body(request)
                request_body = await request.body()
                response = await call_next(request)

                if self.excluded_agents:
                    if any(pattern.match(request.headers.get("User-Agent")) for pattern in self.excluded_agents):
                        return response

                if self.excluded_paths:
                    if any(pattern.fullmatch(request.url.path) for pattern in self.excluded_paths):
                        return response

                data = {
                    "time": datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
                    "realm": os.getenv("REALM", "dev"),
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code,
                    "duration": int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
                }

                if strtobool(os.getenv("FULL_ACCESS_LOG_ENABLED", FULL_ACCESS_LOG_ENABLED)):
                    data["user_agent"] = request.headers.get("User-Agent", "")
                    data["referer"] = request.headers.get("Referer", "")
                    data["user_ip"] = request.headers.get("X-Forwarded-For") if request.headers.get("X-Forwarded-For") else request.client.host
                    data["trace_id"] = request.headers.get("X-Ab-TraceID") if request.headers.get("X-Ab-TraceID") else uuid.uuid4().hex

                    response_body = [chunk async for chunk in response.body_iterator]
                    response.body_iterator = iterate_in_threadpool(iter(response_body))

                    if request.headers.get("Authorization"):
                        data_token = decodeToken(request.headers.get("Authorization"))
                        data["user_id"] = data_token.get("user_id", "")
                        data["client_id"] = data_token.get("client_id", "")
                        data["namespace"] = data_token.get("namespace", "")

                    if request_body:
                        data["request_content_type"] = request.headers.get('content-type')
                        data["request_body"] = getRequestBody(request_body, request.headers.get('content-type'))

                    if response_body[0]:
                        data["length"] = len(response_body[0])
                        data["response_content_type"] = response.headers.get('content-type')
                        data["response_body"] = getResponseBody(response_body[0], response.headers.get('content-type'))

                    logging.info(FULL_LOG_FORMAT.format(
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
                        data.get("response_body", "")
                    ))

                else:

                    logging.info(DEFAULT_LOG_FORMAT.format(
                        data.get("time"),
                        data.get("realm"),
                        data.get("method"),
                        data.get("path"),
                        data.get("status"),
                        data.get("duration")
                    ))

                return response
        
        
    async def set_body(self, request: Request):
        receive_ = await request._receive()

        async def receive() -> Message:
            return receive_

        request._receive = receive
