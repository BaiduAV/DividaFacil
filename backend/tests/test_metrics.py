#!/usr/bin/env python3
"""Tests for metrics endpoint including new status/error counters."""

def test_metrics_basic(client):
    # Trigger a couple of requests
    client.get("/healthz")
    client.get("/api/csrf-token")
    resp = client.get("/metrics")
    body = resp.text.splitlines()
    # Basic gauges
    assert any(line.startswith("app_requests_total ") for line in body)
    assert any(line.startswith("app_request_latency_seconds_sum ") for line in body)
    # Status lines
    assert any(line.startswith("app_requests_status_total{status=") for line in body)
    # Errors counter present
    assert any(line.startswith("app_errors_total ") for line in body)
