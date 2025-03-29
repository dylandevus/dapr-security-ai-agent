### YAML

```
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
```

### SQL Query

```
WITH recent_requests AS (
    SELECT
        endpoint,
        response_code,
        response_time,
        COUNT(*) OVER (PARTITION BY endpoint) AS total_requests,
        COUNT(*) FILTER (WHERE response_code >= 400) OVER (PARTITION BY endpoint) AS error_requests
    FROM
        api_requests
    WHERE
        timestamp >= NOW() - INTERVAL '15 minutes'
),
calculated_metrics AS (
    SELECT
        endpoint,
        (error_requests::FLOAT / total_requests) * 100 AS error_rate_percentage,
        AVG(response_time) AS avg_response_time_ms
    FROM
        recent_requests
    GROUP BY
        endpoint, total_requests, error_requests
)
SELECT
    endpoint
FROM
    calculated_metrics
WHERE
    error_rate_percentage > 5
    AND avg_response_time_ms > 2000;
```

### Kibana Query (KQL)

```
endpoint: "*" AND response_code: >=400 AND response_time: >2000 AND timestamp >= now() - 15m
```