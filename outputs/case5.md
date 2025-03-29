### YAML Configuration

```
id: MON-RESOURCE-UTILIZATION-002
name: Proactive Resource Utilization Monitoring
description: >
  Alert when resource utilization trends towards capacity limits, considering historical usage patterns and growth rates.
target_entity: microservice_resources
conditions:
  - metric: cpu_usage_percentage
    calculation: "average(cpu_usage)"
    threshold:
      value: 80
      condition: '>'
  - metric: memory_usage_percentage
    calculation: "average(memory_usage)"
    threshold:
      value: 75
      condition: '>'
time_window: 1h
considerations:
  - historical_data_review
  - growth_rate_analysis
severity: warning
owner_team: devops_team
runbook_link: /wiki/alerts/MON-RESOURCE-UTILIZATION-002
```

### SQL Query for Historical and Growth Analysis

```
WITH historical_data AS (
    SELECT
        server_id,
        AVG(cpu_usage) AS avg_cpu_usage,
        AVG(memory_usage) AS avg_memory_usage,
        DATE_TRUNC('hour', timestamp) AS hourly_timestamp
    FROM
        system_performance
    WHERE
        timestamp >= NOW() - INTERVAL '1 month'
    GROUP BY
        server_id, hourly_timestamp
),
growth_rate AS (
    SELECT
        server_id,
        MAX(cpu_usage) - MIN(cpu_usage) AS cpu_growth_rate,
        MAX(memory_usage) - MIN(memory_usage) AS memory_growth_rate
    FROM
        historical_data
    GROUP BY
        server_id
)
SELECT
    sp.server_id,
    sp.cpu_usage,
    sp.memory_usage,
    sp.timestamp,
    hr.cpu_growth_rate,
    hr.memory_growth_rate
FROM
    system_performance sp
JOIN
    growth_rate hr ON sp.server_id = hr.server_id
WHERE
    sp.timestamp >= NOW() - INTERVAL '1 hour'
    AND (sp.cpu_usage > 80 OR sp.memory_usage > 75)
    AND (hr.cpu_growth_rate > 0 OR hr.memory_growth_rate > 0)
ORDER BY
    sp.timestamp DESC;
```

### Kibana KQL Query

```
server_id: * AND
(cpu_usage > 80 OR memory_usage > 75) AND
@timestamp >= now-1h AND
(historical_data_review: true AND growth_rate_analysis: true)
```

This setup provides comprehensive definitions for proactive monitoring of microservices, focusing on CPU and memory utilization trends with respect to historical and growth data.