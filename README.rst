=========================
justice-python-common-log
=========================

.. image:: https://img.shields.io/pypi/pyversions/justice_python_common_log
        :target: https://pypi.python.org/pypi/justice_python_common_log
        :alt: Python Version

.. image:: https://img.shields.io/pypi/l/justice_python_common_log
        :target: https://github.com/AccelByte/justice-python-common-log/blob/main/LICENSE
        :alt: License




Justice common log format for python


* Free software: Apache Software License 2.0


Usage in flask
~~~~~~~~~~~~~~

**Basic**

.. code:: python

   import flask
   from justice_python_common_log.flask import Log

   app = flask.Flask(__name__)
   Log(app)


**Exclude specific endpoint**

.. code:: python

   Log(app, excluded_paths=['/swaggerui.*', '/analytics/apidocs'])


**Exclude specific agent**

.. code:: python

   Log(app, excluded_agents=['ELB'])


Usage in FastAPI
~~~~~~~~~~~~~~

**Basic**

.. code:: python

   from fastapi import FastAPI
   from justice_python_common_log.fastapi import Log

   app = FastAPI()
   Log(app)


**Exclude specific endpoint**

.. code:: python

   Log(app, excluded_paths=['/swaggerui.*', '/game-telemetry/apidocs'])


**Exclude specific agent**

.. code:: python

   Log(app, excluded_agents=['ELB'])


Environment variables
~~~~~~~~~~~~~~~~~~~~~

**FULL_ACCESS_LOG_ENABLED**
: Enable full access log mode. Default: *false*.

**FULL_ACCESS_LOG_SUPPORTED_CONTENT_TYPES**
: Supported content types to shown in request_body and response_body log.
Default:
*application/json,application/xml,application/x-www-form-urlencoded,text/plain,text/html*.

**FULL_ACCESS_LOG_MAX_BODY_SIZE**
: Maximum size of request body or response body that will be processed,
will be ignored if exceed more than it. Default: *10240 bytes*
