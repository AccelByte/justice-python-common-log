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

DEFAULT_LOG_FORMAT = 'time={:s} log_type=access method={:s} path={:s} status={:d} duration={:d}'
FULL_LOG_FORMAT = 'time={:s} log_type=access method={:s} path="{:s}" status={:d} duration={:d} length={:d} source_ip={:s} user_agent="{:s}" referer="{:s}" trace_id={:s} namespace={:s} user_id={:s} client_id={:s} request_content_type="{:s}" request_body=AB[{:s}]AB response_content_type="{:s}" response_body=AB[{:s}]AB operation="" flight_id="{:s}" game_version="{:s}" sdk_version="{:s}" oss_version="{:s}"'

FULL_ACCESS_LOG_ENABLED= "False"
FULL_ACCESS_LOG_SUPPORTED_CONTENT_TYPES= "application/json,application/xml,application/x-www-form-urlencoded,text/plain,text/html"
FULL_ACCESS_LOG_MAX_BODY_SIZE= 10240
