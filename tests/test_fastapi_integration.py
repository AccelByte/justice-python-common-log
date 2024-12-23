import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
import logging
import os
from justice_python_common_log.fastapi import Log

class TestFastAPIIntegration:
    @pytest.fixture(autouse=True)
    def setup_logging(self):
        """Setup and cleanup logging for tests"""
        captured_records = []

        class TestHandler(logging.Handler):
            def emit(self, record):
                captured_records.append(record)

        # Get the logger
        logger = logging.getLogger('justice-common-log')

        # Save original settings
        original_level = logger.level
        original_handlers = logger.handlers.copy()

        # Clear any existing handlers and set level
        logger.handlers = []
        logger.setLevel(logging.INFO)

        # Add our test handler
        handler = TestHandler()
        logger.addHandler(handler)

        yield captured_records

        # Restore original settings
        logger.handlers = original_handlers
        logger.setLevel(original_level)

    @pytest.fixture(autouse=True)
    def setup_env(self):
        """Setup and cleanup environment variables"""
        os.environ["FULL_ACCESS_LOG_ENABLED"] = "true"
        yield
        if "FULL_ACCESS_LOG_ENABLED" in os.environ:
            del os.environ["FULL_ACCESS_LOG_ENABLED"]

    @pytest.fixture
    def fastapi_app(self):
        """Create FastAPI test app with middleware"""
        app = FastAPI()

        @app.get("/test")
        async def test_get():
            return {"message": "success"}

        @app.post("/test-post")
        async def test_post(request: Request):
            body = await request.json()
            return body

        @app.post("/test-large-response")
        async def test_large_response():
            # Generate large response
            return {"data": "x" * 20000}

        @app.get("/excluded")
        async def excluded():
            return {"message": "excluded"}

        Log(app, excluded_paths=["/excluded"], excluded_agents=["excluded-agent"])

        return app

    @pytest.fixture
    def test_client(self, fastapi_app):
        return TestClient(fastapi_app)

    def test_large_request_body(self, test_client, setup_logging):
        """Test handling of large request bodies"""
        large_data = {"data": "x" * 20000}  # Exceeds max body size

        response = test_client.post(
            "/test-post",
            json=large_data,
            headers={"Content-Type": "application/json"}
        )

        assert response.status_code == 200
        # Verify original response is not modified
        #
        # print("Response content:", response.content)  # Debug what we actually got
        # print("Response headers:", response.headers)  # Check content-type
        assert response.json() == large_data

        assert len(setup_logging) == 1
        log_record = setup_logging[0]

        # Verify logging behavior for large request
        assert "data too large" in log_record.msg

        # Optionally verify original data isn't in log
        assert "x" * 20000 not in log_record.msg

    def test_large_response_body(self, test_client, setup_logging):
        """Test handling of large response bodies"""
        response = test_client.post("/test-large-response")

        assert response.status_code == 200
        # Verify original response is not modified
        assert len(response.json()["data"]) == 20000

        assert len(setup_logging) == 1
        log_record = setup_logging[0]

        # Verify logging behavior for large response
        assert "data too large" in log_record.msg

        # Optionally verify original data isn't in log
        assert "x" * 20000 not in log_record.msg

    def test_multiple_requests_with_large_bodies(self, test_client, setup_logging):
        """Test multiple consecutive requests with large bodies"""
        for _ in range(3):
            large_data = {"data": "x" * 20000}
            response = test_client.post(
                "/test-post",
                json=large_data,
                headers={"Content-Type": "application/json"}
            )
            assert response.status_code == 200
            assert response.json() == large_data

        assert len(setup_logging) == 3
        for log_record in setup_logging:
            assert "data too large" in log_record.msg
            assert "x" * 20000 not in log_record.msg
