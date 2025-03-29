from dapr_agents import tool, ReActAgent
from dotenv import load_dotenv
from config import SQL_SCHEMAS, YAML_TEMPLATE_SAMPLE

load_dotenv()


@tool
def generate_yaml(user_prompt: str) -> str:
    """Generate YAML configuration template file."""
    yaml_string = f"""Generate a YAML file. This file will be used to create SQL and Kibana KQL queries to retrieve results for the user.

    Below is an example of a YAML configuration template file:

    ```
    {YAML_TEMPLATE_SAMPLE}
    ```
    """
    return yaml_string


@tool
def generate_sql(yaml_string: str) -> str:
    """Generate a SQL query and Kibana query (KQL) to get data for security analytics."""
    query_string = f"""
        YAML configuration template is provided below:
        
        ```
        {yaml_string}
        ```

        The database schemas are provided below:

        ```
        {SQL_SCHEMAS}
        ```
        
        Generating SQL queries, prioritize performance and utilize techniques such as Common Table Expressions (CTEs) to enhance portability and readability.

        Also generate Kibana query (KQL).
    """
    return query_string


react_agent = ReActAgent(
    name="SecurityAIAgent",
    role="Security AI Agent",
    instructions=[
        """
        You are a Security AI Agent, an application health monitoring system. Your task is to take user prompts in natural language.
        """
    ],
    tools=[generate_yaml, generate_sql],
)

# prompt = "Create a query to alert when any API endpoint experiences a 50% increase in average response time compared to the previous hour's baseline."
prompt = "Users have reported unusual account activity. Create monitoring to detect anomalous user session patterns that could indicate account compromise. Consider factors like login frequency, concurrent sessions, and access patterns."
# prompt = "Monitor for scenarios where error rates exceed 5% of total requests per endpoint while also having high response times (>2s) in the last 15 minutes."
# prompt = "The application seems slow during peak hours (working business hours). Create a query to help us understand what's causing it."

result = react_agent.run(prompt)

if len(result) > 0:
    print("Result:", result)

for item in react_agent.chat_history:
    print(item, "\n\n")
