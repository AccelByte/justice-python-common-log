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

.. code:: python

   from justice_python_common_log.flask import Log
   import flask

   app = flask.Flask(__name__)
   log = Log(app)



Environment variables
~~~~~~~~~~~~~~~~~~~~~

**FULL_ACCESS_LOG_ENABLED** 
=> Enable full access log mode. Default: *false*.

**FULL_ACCESS_LOG_SUPPORTED_CONTENT_TYPES**
=> Supported content types to shown in request_body and response_body log.
Default:
*application/json,application/xml,application/x-www-form-urlencoded,text/plain,text/html*.

**FULL_ACCESS_LOG_MAX_BODY_SIZE**
=> Maximum size of request body or response body that will be processed,
will be ignored if exceed more than it. Default: *10240 bytes*
