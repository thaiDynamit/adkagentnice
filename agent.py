# masterpiece_agent/agent.py

import os # Required for path operations
from google.adk.agents import Agent
# For MCP Tool integration
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters

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

# Define the target folder for the MCP File System Server
# This will be a directory named 'mcp_filesystem_root' in the same directory as this agent.py file.
# The MCP server will have access to this directory.
MCP_TARGET_FOLDER_NAME = "mcp_filesystem_root"
TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), MCP_TARGET_FOLDER_NAME)
# Ensure the path is absolute for the MCP server
ABSOLUTE_TARGET_FOLDER_PATH = os.path.abspath(TARGET_FOLDER_PATH)

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

# Architect agent now includes MCPToolset for file system operations
architect_agent = Agent(
    name="architect_agent",
    model="gemini-1.5-pro-latest",
    instruction="You are a Software Architect. Design the tech stack and database schema. "
                "You can also read files to understand existing project structures using local tools, "
                "and interact with a dedicated file system via MCP tools (e.g., list files, read files from the MCP directory). "
                f"The MCP file system is rooted at '{MCP_TARGET_FOLDER_NAME}'.",
    tools=[
        suggest_tech_stack,
        design_database_schema,
        read_file_content, # Existing file reading tool
        MCPToolset(
            connection_params=StdioServerParameters(
                command='npx',
                args=[
                    "-y",  # Argument for npx to auto-confirm install
                    "@modelcontextprotocol/server-filesystem",
                    # IMPORTANT: This MUST be an ABSOLUTE path.
                    ABSOLUTE_TARGET_FOLDER_PATH,
                ],
            ),
            # Optional: Filter which tools from the MCP server are exposed
            # tool_filter=['list_directory', 'read_file']
        )
    ],
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
