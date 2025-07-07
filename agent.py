# masterpiece_agent/masterpiece_agents.py

from google.adk.agent import Agent
# ✅ This import now points to your uniquely named tools file.
from .tools import (
    suggest_tech_stack,
    design_database_schema,
    create_user_stories,
    generate_swift_code,
    generate_kotlin_code,
    review_code_for_bugs,
    write_unit_tests,
    read_file_content,
    add_placeholder_data,
    get_design_tool_instructions,
    suggest_alternative_tools,
    create_directory,
    create_file,
    list_files,
    run_command
)

# 1. SPECIALISTS
qa_agent = Agent(
    name="qa_agent",
    model="gemini-1.5-pro-latest",
    instruction="You are a QA Engineer. You review code for bugs and write unit tests.",
    tools=[review_code_for_bugs, write_unit_tests]
)

swift_coder_agent = Agent(
    name="swift_coder_agent",
    model="gemini-1.5-pro-latest",
    instruction="You are an expert Swift developer. You write clean Swift code for iOS apps.",
    tools=[generate_swift_code]
)

kotlin_coder_agent = Agent(
    name="kotlin_coder_agent",
    model="gemini-1.5-pro-latest",
    instruction="You are an expert Kotlin developer. You write clean, idiomatic Kotlin code for Android apps.",
    tools=[generate_kotlin_code]
)

# 2. TEAM LEADS
engineer_lead_agent = Agent(
    name="engineer_lead_agent",
    model="gemini-1.5-pro-latest",
    instruction="You are an Engineering Lead. Break down features and delegate to your coders based on the required platform (Swift for iOS, Kotlin for Android). Then, send the code to the QA agent for review.",
    sub_agents=[swift_coder_agent, kotlin_coder_agent, qa_agent]
)

architect_agent = Agent(
    name="architect_agent",
    model="gemini-1.5-pro-latest",
    instruction="You are a Software Architect. Design the tech stack and database schema. You can also read files to understand existing project structures and call remote tools for more information.",
    tools=[suggest_tech_stack, design_database_schema, read_file_content],
    mcp_servers=[{
        "url": "http://localhost:8001",
        "headers": {
            "X-Auth-Token": "your-secret-tool-server-key",
            "Content-Type": "application/json"
        }
    }],
    sub_agents=[engineer_lead_agent]
)

# 3. TOP-LEVEL AGENT, NAMED 'root_agent'
root_agent = Agent(
    name="root_agent",
    model="gemini-1.5-pro-latest",
    instruction="You are a Product Manager. Understand the user's app idea, create a plan, then hand it off to the Architect.",
    tools=[create_user_stories],
    sub_agents=[architect_agent]
)