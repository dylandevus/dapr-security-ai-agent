from dapr_agents import tool, ReActAgent
from dotenv import load_dotenv
from config import SQL_SCHEMAS

load_dotenv()


@tool
def generate_yaml(user_prompt: str) -> str:
    """Generate yaml file content."""
    yaml_str = "yaml file content"
    return yaml_str


@tool
def generate_sql(yaml_str: str) -> str:
    """Generate a SQL query to get data for security analytics."""
    sql_str = "SQL SELECT Query"
    return sql_str


react_agent = ReActAgent(
    name="SecurityAIAgent",
    role="Security AI Agent",
    instructions=[
        "You are a Security AI Agent - an application health monitoring system. Your task is taking user's prompt in natural language, generate a yaml file that will be used to generate SQL queries (or Kibana KQL, PromQL, etc.) to get results for that user. Provide the Database Schemas below: "
        + SQL_SCHEMAS
    ],
    tools=[generate_yaml, generate_sql],
)

result = react_agent.run(
    "Create a query to alert when any API endpoint experiences a 50% increase in average response time compared to the previous hour's baseline."
)

if len(result) > 0:
    print("Result:", result)
