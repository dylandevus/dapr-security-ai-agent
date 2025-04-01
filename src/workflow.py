# from dapr_agents.workflow import WorkflowApp, workflow, task
import dapr.ext.workflow as wf
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from utils import remove_double_quotes
from config import SQL_SCHEMAS, YAML_TEMPLATE_SAMPLE

# Load environment variables
load_dotenv()

# Initialize Workflow Instance
wfr = wf.WorkflowRuntime()

MODEL = "gpt-4o"
DEFAULT_PROMPT = f"""
You are a Security AI Agent, an application health monitoring system.
You have access to database schemas and YAML blueprint examples for generating SQL, KQL, and PromQL queries.

The database schemas are provided below:

```
{SQL_SCHEMAS}
```
"""


# Define Workflow logic
@wfr.workflow(name="task_chain_workflow")
def task_chain_workflow(ctx: wf.DaprWorkflowContext, query: str):
    yaml = yield ctx.call_activity(generate_yaml, input=query)
    sql = yield ctx.call_activity(generate_sql, input=yaml)
    kql = yield ctx.call_activity(generate_kql, input=yaml)
    return yaml + "\n\n---\n\n" + sql + "\n\n---\n\n" + kql


# Activity 1
@wfr.activity(name="step1")
def generate_yaml(ctx, activity_input: str):
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"""{DEFAULT_PROMPT}

                    Below is one example of a YAML structured blueprint: (for reference only)

                    ```
                    {YAML_TEMPLATE_SAMPLE}
                    ```

                    Generate a new YAML structured blueprint, output only YAML content (no formatting, no triple backticks, etc.),
                    follows closely the database schemas above and the user's prompt in natural language below:
                    
                    User's prompt: {activity_input}""",
                }
            ],
            model=MODEL,
        )
        content = response.choices[0].message.content
        return content
    except Exception as e:
        print(f"Error in generate_yaml: {e}")
        return f"Error in generate_yaml: {e}"


# Activity 2
@wfr.activity(name="step2")
def generate_sql(ctx, yaml_template: str):
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"""{DEFAULT_PROMPT}

                    The generated YAML structured blueprint is below:

                    ```
                    {yaml_template}
                    ```
                    
                    Generate SQL query only (no formatting, no backticks, no markdown, etc.), prioritize performance
                    and utilize techniques such as Common Table Expressions (CTEs) to enhance portability and readability.
                    """,
                }
            ],
            model=MODEL,
        )
        content = response.choices[0].message.content
        print(f"--- SQL QUERY: {content}")
        return content
    except Exception as e:
        print(f"Error in generate_sql: {e}")
        return f"Error in generate_sql: {e}"


# Activity 3
@wfr.activity(name="step3")
def generate_kql(ctx, yaml_template: str):
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"""{DEFAULT_PROMPT}

                    The generated YAML structured blueprint is below:

                    ```
                    {yaml_template}
                    ```
                    
                    Generate Kibana KQL query only (no formatting, no backticks, no markdown, etc.), prioritize performance
                    and enhance portability and readability.
                    """,
                }
            ],
            model=MODEL,
        )
        content = response.choices[0].message.content
        print(f"--- KQL QUERY: {content}")
        return content
    except Exception as e:
        print(f"Error in generate_sql: {e}")
        return f"Error in generate_sql: {e}"


app = FastAPI()


@app.get("/run")
async def run(q: str):
    try:
        wf_client = wf.DaprWorkflowClient()
        instance_id = wf_client.schedule_new_workflow(
            workflow=task_chain_workflow, input=q
        )

        print(f"Workflow started. Instance ID: {instance_id}")
        state = wf_client.wait_for_workflow_completion(instance_id)
        print(f"Workflow completed! Status: {state.runtime_status}")

        # wfr.shutdown()

        output = state.serialized_output.replace("\\n", "\n").replace("\\t", "\t")
        output = remove_double_quotes(output)
        return HTMLResponse(
            content=f"<pre style='text-wrap: wrap;'>{output}</pre>", status_code=200
        )

        # wfapp = WorkflowApp()
        # results = wfapp.run_and_monitor_workflow(task_chain_workflow)
        # return results

    except Exception as e:
        print(f"Error in /run: {e}")
        return HTMLResponse(
            content=f"<h1>Error in /run</h1><p>{e}</p>", status_code=500
        )
