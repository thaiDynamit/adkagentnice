# masterpiece_agent/agent.py

from google.adk.agents import Agent
from .tools import (
    suggest_tech_stack,
    design_database_schema,
    create_user_stories,
    generate_swift_code,
    generate_kotlin_code,
    review_code_for_bugs,
    write_unit_tests,
    read_file_content
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

# ✅ CORRECTED: The MCP client and configuration have been completely removed.
architect_agent = Agent(
    name="architect_agent",
    model="gemini-1.5-pro-latest",
    instruction="You are a Software Architect. Design the tech stack and database schema. You can also read files to understand existing project structures.",
    tools=[suggest_tech_stack, design_database_schema, read_file_content],
    sub_agents=[engineer_lead_agent]
)

# 3. TOP-LEVEL AGENT, NAMED 'root_agent'
root_agent = Agent(
    name="product_manager_agent",
    model="gemini-1.5-pro-latest",
    instruction="You are a Product Manager. Understand the user's app idea, create a plan, then hand it off to the Architect.",
    tools=[create_user_stories],
    sub_agents=[architect_agent]
)
