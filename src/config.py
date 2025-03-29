# --- SQL Schema Definition ---
# Provide the schemas as a string for the agent's context
SQL_SCHEMAS = """ 
CREATE TABLE user_sessions (
    session_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36),
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    ip_address VARCHAR(45),
    browser_type VARCHAR(100),
    device_type VARCHAR(50),
    status VARCHAR(20) -- e.g., active, ended, expired
);

CREATE TABLE application_errors (
    error_id VARCHAR(36) PRIMARY KEY,
    timestamp TIMESTAMP,
    error_code VARCHAR(50),
    error_message VARCHAR(500),
    severity_level VARCHAR(20), -- e.g., info, warning, error, critical
    module_name VARCHAR(100),
    user_id VARCHAR(36),
    session_id VARCHAR(36),
    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id)
);

CREATE TABLE system_performance (
    metric_id VARCHAR(36) PRIMARY KEY,
    timestamp TIMESTAMP,
    cpu_usage DECIMAL(5,2),
    memory_usage DECIMAL(5,2),
    disk_usage DECIMAL(5,2),
    response_time DECIMAL(10,3), -- in milliseconds
    active_connections INTEGER,
    server_id VARCHAR(36)
);

CREATE TABLE api_requests (
    request_id VARCHAR(36) PRIMARY KEY,
    timestamp TIMESTAMP,
    endpoint VARCHAR(200),
    method VARCHAR(10), -- GET, POST, PUT, DELETE, etc.
    response_code INTEGER,
    response_time DECIMAL(10,3), -- in milliseconds
    user_id VARCHAR(36),
    session_id VARCHAR(36),
    payload_size INTEGER, -- in bytes
    FOREIGN KEY (session_id) REFERENCES user_sessions(session_id)
);

CREATE TABLE resource_utilization (
    resource_id VARCHAR(36) PRIMARY KEY,
    timestamp TIMESTAMP,
    resource_type VARCHAR(50), -- e.g., CPU, Memory, Disk I/O, Network Bandwidth
    current_usage DECIMAL(10,2),
    max_capacity DECIMAL(10,2),
    server_id VARCHAR(36),
    status VARCHAR(20) -- e.g., ok, warning, critical
);
"""

YAML_TEMPLATE_SAMPLE = """
id: MON-API-ERRORS-AND-LATENCY-001
name: High API Error Rate (>5%) and Latency (>2s)
description: >
  Alert when any API endpoint experiences both an error rate exceeding 5% AND
  an average response time greater than 2000ms over the last 15 minutes.
target_entity: api_requests.endpoint
conditions: # Multiple conditions must be met (AND logic)
  - metric: error_rate_percentage
    calculation: "(count(response_code >= 400) / count(*)) * 100"
    threshold:
      value: 5
      condition: '>'
  - metric: avg_response_time_ms
    aggregation: average(response_time)
    threshold:
      value: 2000
      condition: '>'
time_window: 15m
minimum_traffic_threshold: # Optional
  metric: request_count
  window: 15m
  threshold: 10
severity: critical
owner_team: backend_reliability
runbook_link: /wiki/alerts/MON-API-ERRORS-AND-LATENCY-001
"""
