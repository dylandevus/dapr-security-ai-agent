### YAML Configuration
```yaml
id: MON-ANOMALOUS-USER-SESSIONS
name: Anomalous User Session Patterns Detection
description: >
  Detect anomalous user session patterns indicating potential account compromise, based on unusual login frequency, concurrent sessions, and access patterns.
target_entity: user_sessions.user_id
conditions: # Multiple conditions must be met (OR logic)
  - metric: unusual_login_frequency
    calculation: "count(*) / unique(user_id)"
    threshold:
      value: 3
      condition: '>'
  - metric: concurrent_sessions
    calculation: "max(count_concurrent_sessions)"
    threshold:
      value: 1
      condition: '>'
  - metric: unusual_access_patterns
    calculation: "distinct(ip_address, browser_type, device_type) / unique(user_id)"
    threshold:
      value: 5
      condition: '>'
time_window: 1h
minimum_traffic_threshold: # Optional
  metric: session_count
  window: 1h
  threshold: 10
severity: high
owner_team: security_team
runbook_link: /wiki/alerts/MON-ANOMALOUS-USER-SESSIONS
```

### SQL Query
```sql
WITH UserSessionStats AS (
    SELECT 
        user_id,
        COUNT(*) AS login_count,
        MAX(end_time) - MIN(start_time) AS session_duration,
        COUNT(DISTINCT user_id) AS user_count,
        MAX(session_count) AS max_concurrent_sessions,
        COUNT(DISTINCT ip_address, browser_type, device_type) AS access_pattern_count
    FROM user_sessions
    WHERE start_time > NOW() - INTERVAL '1 hour'
    GROUP BY user_id
)
SELECT * FROM UserSessionStats
WHERE (login_count / user_count) > 3
   OR max_concurrent_sessions > 1
   OR (access_pattern_count / user_count) > 5
```

### Kibana Query (KQL)
```kql
user_sessions : { start_time > now() - 1h } 
| stats count() as login_count, 
        unique_count(user_id) as user_count,
        max(concurrent_sessions) as max_concurrent_sessions,
        unique_count(ip_address, browser_type, device_type) as access_pattern_count 
by user_id 
| where (login_count / user_count) > 3 
   or max_concurrent_sessions > 1 
   or (access_pattern_count / user_count) > 5
```