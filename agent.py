# masterpiece_agent/agent.py

import os # Required for path operations
from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioConnectionParams # Updated import
# Changed from relative to absolute import for tools
import tools

# Define a path for the MCP server to access.
# This will be a subdirectory within the project.
TARGET_FOLDER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mcp_filesystem_data")
# Ensure the TARGET_FOLDER_PATH is absolute.
ABSOLUTE_TARGET_FOLDER_PATH = os.path.abspath(TARGET_FOLDER_PATH)

# --- Start Debugging Prints ---
print("--- AGENT SCRIPT START ---")
print(f"Current Working Directory: {os.getcwd()}")
print(f"Absolute Path for MCP: {ABSOLUTE_TARGET_FOLDER_PATH}")
print(f"Script Path: {__file__}")
# print(f"System PATH variable: {os.environ.get('PATH')}") # This can be very long, uncomment if needed
print("--- END DEBUGGING PRINTS ---")


# 1. SPECIALISTS
qa_agent = Agent(
    name="qa_agent",
    model="gemini-1.5-pro-latest",
    instruction="You are a QA Engineer. You review code for bugs and write unit tests.",
    tools=[tools.review_code_for_bugs, tools.write_unit_tests]
)

swift_coder_agent = Agent(
    name="swift_coder_agent",
    model="gemini-1.5-pro-latest",
    instruction="You are an expert Swift developer. You write clean Swift code for iOS apps.",
    tools=[tools.generate_swift_code]
)

kotlin_coder_agent = Agent(
    name="kotlin_coder_agent",
    model="gemini-1.5-pro-latest",
    instruction="You are an expert Kotlin developer. You write clean, idiomatic Kotlin code for Android apps.",
    tools=[tools.generate_kotlin_code]
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
    instruction="You are a Software Architect. Design the tech stack and database schema. You can also read files to understand existing project structures and manage files using MCP.",
    tools=[
        tools.suggest_tech_stack,
        tools.design_database_schema,
        tools.read_file_content,
        tools.list_mcp_files, # Added the new MCP tool here as well
        MCPToolset(
            connection_params=StdioConnectionParams(
                # Using cmd.exe /c with the full path to npx.cmd for Windows robustness
                command='cmd.exe',
                args=[
                    '/c', # Tells cmd.exe to execute the command and then terminate
                    'C:\\Program Files\\nodejs\\npx.cmd', # Full path from user
                    "-y",
                    "@modelcontextprotocol/server-filesystem",
                    # Using a version of the path with forward slashes for better compatibility
                    ABSOLUTE_TARGET_FOLDER_PATH.replace('\\', '/'),
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
    tools=[tools.create_user_stories],
    sub_agents=[architect_agent]
)

# Test function for MCP integration
if __name__ == '__main__':
    import asyncio
    import sys
    import os

    # Ensure the script's directory is in sys.path to allow importing `tools`
    # This helps when running the script directly.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

    # The main agent definitions above now use absolute imports `tools.X`,
    # which works when running directly or via `adk web`.
    # The test harness can also use `tools.list_mcp_files`.

    from google.adk.runners import Runner
    from google.adk.sessions import InMemorySessionService # Import session service
    # from google.adk.sessions import Session # Session objects are created by the service
    from google.genai import types

    async def run_mcp_test():
        print("Starting MCP integration test...")
        # Ensure the mcp_filesystem_data directory and test file exist
        # Note: ABSOLUTE_TARGET_FOLDER_PATH is defined at the top of the file
        if not os.path.exists(ABSOLUTE_TARGET_FOLDER_PATH):
            os.makedirs(ABSOLUTE_TARGET_FOLDER_PATH)
            print(f"Created directory: {ABSOLUTE_TARGET_FOLDER_PATH}")
        test_file_path = os.path.join(ABSOLUTE_TARGET_FOLDER_PATH, "test_file_from_script.txt")
        if not os.path.exists(test_file_path):
            with open(test_file_path, "w") as f:
                f.write("This is a test file created by the agent.py script.")
            print(f"Created test file: {test_file_path}")

        # Initialize session service
        session_service = InMemorySessionService()

        # Use a simple runner for testing
        runner = Runner(
            app_name="mcp_test_app",
            agent=architect_agent,
            session_service=session_service # Pass session_service
        )
        # Create session using the service
        session = await session_service.create_session(
            app_name="mcp_test_app", user_id="test_user"
        )
        print(f"Created session: {session.id}")


        # Prompt the architect_agent to use the MCP tool
        # The list_mcp_files tool returns a string that instructs the agent.
        # The agent then uses its MCPToolset.
        prompt_text = tools.list_mcp_files("List files in your designated folder.")

        print(f"Generated prompt for agent: {prompt_text}")

        # Create content object for the runner
        content = types.Content(role='user', parts=[types.Part(text=prompt_text)])

        print("Invoking architect_agent with MCP prompt...")
        try:
            async for event in runner.run_async(
                session_id=session.id,
                user_id=session.user_id,
                new_message=content
            ):
                print(f"Agent Event: {event.type}")
                if event.type == "tool_code":
                    print(f"  Tool Code: {event.data.tool_code}")
                elif event.type == "tool_result":
                    print(f"  Tool Result ({event.data.tool_name}): {event.data.result}")
                elif event.type == "model_response":
                    print(f"  Model Response: {event.data.text}")
                elif event.type == "error":
                    print(f"  Error: {event.data.message}")
        except Exception as e:
            print(f"An error occurred during agent execution: {e}")
        finally:
            # MCPToolset has a close method that should be called to terminate the subprocess
            for tool in architect_agent.tools:
                if isinstance(tool, MCPToolset):
                    await tool.close()
            print("MCP Toolset closed.")

        print("MCP integration test finished.")

    asyncio.run(run_mcp_test())
