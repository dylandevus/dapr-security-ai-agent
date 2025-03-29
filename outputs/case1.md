**YAML**

```
id: MON-API-RESPONSE-TIME-INCREASE-001
name: API Response Time Increase > 50%
description: >
  Alert when any API endpoint experiences a 50% increase in average response time
  compared to the previous hour's baseline.
target_entity: api_requests.endpoint
conditions:
  - metric: avg_response_time_increase_percentage
    calculation: "((current_avg_response_time - baseline_avg_response_time) / baseline_avg_response_time) * 100"
    threshold:
      value: 50
      condition: '>'
time_window: 1h
severity: high
owner_team: backend_reliability
runbook_link: /wiki/alerts/MON-API-RESPONSE-TIME-INCREASE-001
```

**SQL Query:**

```
WITH Baseline AS (
    SELECT
        endpoint,
        AVG(response_time) AS baseline_avg_response_time
    FROM
        api_requests
    WHERE
        timestamp BETWEEN NOW() - INTERVAL '2 HOURS' AND NOW() - INTERVAL '1 HOUR'
    GROUP BY
        endpoint
),
CurrentHour AS (
    SELECT
        endpoint,
        AVG(response_time) AS current_avg_response_time
    FROM
        api_requests
    WHERE
        timestamp BETWEEN NOW() - INTERVAL '1 HOUR' AND NOW()
    GROUP BY
        endpoint
)
SELECT
    CurrentHour.endpoint,
    ((CurrentHour.current_avg_response_time - Baseline.baseline_avg_response_time) / Baseline.baseline_avg_response_time) * 100 AS avg_response_time_increase_percentage
FROM
    CurrentHour
JOIN
    Baseline ON CurrentHour.endpoint = Baseline.endpoint
WHERE
    ((CurrentHour.current_avg_response_time - Baseline.baseline_avg_response_time) / Baseline.baseline_avg_response_time) * 100 > 50;
```

**Kibana Query Language (KQL):**

```
let baseline_avg_response_time = average(response_time) ['2h'] to ['1h'];
let current_avg_response_time = average(response_time) ['1h'];
where endpoint != null and
((current_avg_response_time - baseline_avg_response_time) / baseline_avg_response_time) * 100 > 50
| stats current_avg_response_time, baseline_avg_response_time, avg_response_time_increase_percentage by endpoint
```

These queries assess the API endpoint's response time for significant increases, triggering alerts for increases exceeding 50% over the last hour's average compared to the immediate prior hour.