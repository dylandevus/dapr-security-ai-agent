import dapr.ext.workflow as wf
from dotenv import load_dotenv
from openai import OpenAI
from time import sleep
from config import SQL_SCHEMAS, YAML_TEMPLATE_SAMPLE

# Load environment variables
load_dotenv()

# Initialize Workflow Instance
wfr = wf.WorkflowRuntime()


# Define Workflow logic
@wfr.workflow(name="task_chain_workflow")
def task_chain_workflow(ctx: wf.DaprWorkflowContext):
    result1 = yield ctx.call_activity(generate_yaml)
    result2 = yield ctx.call_activity(generate_sql, input=result1)
    return result2


# Activity 1
@wfr.activity(name="step1")
def generate_yaml(ctx):
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

                Generate a YAML structured blueprint, output only YAML content (no triple backticks), follows closely the database schemas above and the user's prompt in natural language below:
                
                User's prompt: create proactive monitoring for resource utilization across our microservices. We need early warning when any service is trending towards capacity limits, considering historical usage patterns and growth rates.""",
            }
        ],
        model="gpt-4o",
    )
    content = response.choices[0].message.content
    return content


# Activity 2
@wfr.activity(name="step2")
def generate_sql(ctx, yaml_template: str):
    client = OpenAI()
    response = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""You are a Security AI Agent, an application health monitoring system. Your task is to take user prompts in natural language.
                
                The database schemas are provided below:

                ```
                {SQL_SCHEMAS}
                ```

                The generated YAML structured blueprint is below:

                ```
                {yaml_template}
                ```
                
                Generating SQL query, prioritize performance and utilize techniques such as Common Table Expressions (CTEs) to enhance portability and readability.

                Also generate Kibana query (KQL). """,
            }
        ],
        model="gpt-4o",
    )
    content = response.choices[0].message.content
    print(f"--- QUERY: {content}")
    return content


if __name__ == "__main__":
    wfr.start()
    sleep(5)  # wait for workflow runtime to start

    wf_client = wf.DaprWorkflowClient()
    instance_id = wf_client.schedule_new_workflow(workflow=task_chain_workflow)
    print(f"Workflow started. Instance ID: {instance_id}")
    state = wf_client.wait_for_workflow_completion(instance_id)
    print(f"Workflow completed! Status: {state.runtime_status}")

    wfr.shutdown()
