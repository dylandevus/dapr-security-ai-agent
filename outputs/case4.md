**YAML**

```yaml
id: MON-SLOW-APP-PEAK-HOURS-001
name: Application Slowness During Peak Hours
description: >
  Collect data on system performance, resource utilization, and API requests
  during peak hours (working business hours) to identify causes of slowness.
target_entities:
  - system_performance
  - resource_utilization
  - api_requests
conditions:
  - time_window: 9:00-17:00 # Working business hours in local time
metrics:
  - system_performance:
      - cpu_usage
      - memory_usage
      - response_time
      - active_connections
  - resource_utilization:
      - current_usage
      - status
  - api_requests:
      - response_time
      - endpoint
      - method
severity: informational
owner_team: operations_team
runbook_link: /wiki/alerts/MON-SLOW-APP-PEAK-HOURS-001
```

**SQL Query:**

```
WITH PeakHours AS (
    SELECT *
    FROM system_performance
    WHERE EXTRACT(HOUR FROM timestamp) BETWEEN 9 AND 17
),
ResourceUtilization AS (
    SELECT *
    FROM resource_utilization
    WHERE EXTRACT(HOUR FROM timestamp) BETWEEN 9 AND 17
),
ApiRequests AS (
    SELECT *
    FROM api_requests
    WHERE EXTRACT(HOUR FROM timestamp) BETWEEN 9 AND 17
)
SELECT 
    ph.timestamp,
    ph.cpu_usage,
    ph.memory_usage,
    ph.response_time AS system_response_time,
    ph.active_connections,
    ru.current_usage AS resource_current_usage,
    ru.status AS resource_status,
    ar.endpoint AS api_endpoint,
    ar.response_time AS api_response_time,
    ar.method AS api_method
FROM 
    PeakHours ph
JOIN 
    ResourceUtilization ru ON ph.timestamp = ru.timestamp
JOIN 
    ApiRequests ar ON ph.timestamp = ar.timestamp;
```

**Kibana KQL Query:**

```
(system_performance.timestamp >= now-1d and system_performance.timestamp < now and 
  extractHour(system_performance.timestamp) >= 9 and 
  extractHour(system_performance.timestamp) <= 17) OR 
(resource_utilization.timestamp >= now-1d and resource_utilization.timestamp < now and 
  extractHour(resource_utilization.timestamp) >= 9 and 
  extractHour(resource_utilization.timestamp) <= 17) OR 
(api_requests.timestamp >= now-1d and api_requests.timestamp < now and 
  extractHour(api_requests.timestamp) >= 9 and 
  extractHour(api_requests.timestamp) <= 17)
```

These queries focus on gathering performance and utilization data during working business hours (9 AM to 5 PM) to help identify potential issues causing application slowness. You can use them in your respective SQL-based and Kibana tools for analysis.