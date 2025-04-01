# from dapr_agents.workflow import WorkflowApp, workflow, task
import dapr.ext.workflow as wf
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from config import SQL_SCHEMAS, YAML_TEMPLATE_SAMPLE

# Load environment variables
load_dotenv()

# Initialize Workflow Instance
wfr = wf.WorkflowRuntime()


# Define Workflow logic
@wfr.workflow(name="task_chain_workflow")
def task_chain_workflow(ctx: wf.DaprWorkflowContext, query: str):
    result1 = yield ctx.call_activity(generate_yaml, input=query)
    result2 = yield ctx.call_activity(generate_sql, input=result1)
    return result2


# Activity 1
@wfr.activity(name="step1")
def generate_yaml(ctx, activity_input: str):
    try:
        client = OpenAI()
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": f"""You are a Security AI Agent, an application health monitoring system.
                    
                    The database schemas are provided below:

                    ```
                    {SQL_SCHEMAS}
                    ```

                    Below is an example of a YAML structured blueprint: (for reference only)

                    ```
                    {YAML_TEMPLATE_SAMPLE}
                    ```

                    Generate a YAML structured blueprint, output only YAML content (no formatting, no triple backticks, etc.),
                    follows closely the database schemas above and the user's prompt in natural language below:
                    
                    User's prompt: {activity_input}""",
                }
            ],
            model="gpt-4o",
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
                    "content": f"""You are a Security AI Agent, an application health monitoring system.
                    
                    The database schemas are provided below:

                    ```
                    {SQL_SCHEMAS}
                    ```

                    The generated YAML structured blueprint is below:

                    ```
                    {yaml_template}
                    ```
                    
                    Generate SQL query only (no formatting, no backticks, no markdown, etc.), prioritize performance
                    and utilize techniques such as Common Table Expressions (CTEs) to enhance portability and readability.
                    """,
                }
            ],
            model="gpt-4o",
        )
        content = response.choices[0].message.content
        print(f"--- QUERY: {content}")
        return content
    except Exception as e:
        print(f"Error in generate_sql: {e}")
        return f"Error in generate_sql: {e}"


# from fastapi import FastAPI

app = FastAPI()

# wf_client = None
# wfr.start()
# sleep(5)  # wait for workflow runtime to start
# wf_client = wf.DaprWorkflowClient()


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

        # print("state", state)
        # wfr.shutdown()

        output = state.serialized_output.replace("\\n", "\n").replace("\\t", "\t")
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
