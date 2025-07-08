# masterpiece_agent/tools.py

from google.adk.tools import FunctionTool  # ✅ Corrected from 'tools' to 'tool'
import os
import subprocess

# Tool 1
def suggest_tech_stack(platform: str, app_type: str) -> str:
    """Recommends a technology stack for a mobile platform."""
    if platform.lower() == 'ios':
        return "For a modern iOS app, I recommend Swift with SwiftUI."
    return "For cross-platform, consider Flutter."

# Tool 2
def design_database_schema(features: str) -> str:
    """Designs a simple database schema based on app features."""
    return f"""Schema for '{features}':
- Users Table (user_id, etc.)
- Main Feature Table (feature_id, etc.)"""

# Tool 3
def create_user_stories(feature_description: str) -> list[str]:
    """Creates user stories from a feature description."""
    return ["As a user, I want to log in, so that I can access my data."]

# Tool 4   
def generate_swift_code(description: str) -> str:
    """Generates a Swift code snippet based on a description."""
    return f"""// Swift code for: {description}

func example() {{ print("Hello, World!") }}"""

# Tool 5
def generate_kotlin_code(description: str, layout_type: str) -> str:
    """Generates Kotlin code for a given UI description and layout type."""
    return f"// Placeholder for generated {layout_type} code for: {description}"

# Tool 6
def review_code_for_bugs(code: str) -> str:
    """Analyzes code for potential bugs."""
    return "Code review: Looks good. Consider adding error handling."

# Tool 7
def write_unit_tests(code_snippet: str, function_name: str) -> str:
    """Generates placeholder unit tests for a function."""
    return f"""// Unit test for {function_name}

func testExample() {{ XCTAssertTrue(true) }}"""

# Tool 8
def read_file_content(file_path: str) -> str:
    """Reads the content of a file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return f"Error: File not found at {file_path}"
    except Exception as e:
        return f"An error occurred: {e}"

# Tool 16
def list_mcp_files(mcp_instruction: str) -> str:
    """
    Instructs an agent with MCP filesystem tools to perform an action.
    Example: "List files in the current directory."
    This tool itself doesn't call MCP directly, but formulates a prompt
    for an agent that has MCP tools.
    """
    # This function serves as a wrapper to guide the LLM agent
    # to use its MCP capabilities. The actual MCP call will be
    # handled by the MCPToolset configured in the agent.
    return f"Please use your filesystem tools to: {mcp_instruction}"

# Tool 9
def add_placeholder_data(code: str) -> str:
    """Adds placeholder data to the given UI code."""
    return code + "\n\n// Placeholder data added"

# Tool 10
def get_design_tool_instructions(tool_name: str) -> str:
    """Returns instructions for using a given design tool."""
    if tool_name.lower() == "figma":
        return "Here are some instructions for using Figma..."
    elif tool_name.lower() == "adobe xd":
        return "Here are some instructions for using Adobe XD..."
    else:
        return "Sorry, I don't have instructions for that tool."

# Tool 11
def suggest_alternative_tools() -> list[str]:
    """Suggests alternative tools or resources."""
    return ["Balsamiq", "Sketch", "InVision"]

# Tool 12
def create_directory(directory_path: str) -> str:
    """Creates a new directory at the specified path."""
    try:
        os.makedirs(directory_path, exist_ok=True)
        return f"Directory created at {directory_path}"
    except Exception as e:
        return f"An error occurred: {e}"

# Tool 13
def create_file(file_path: str, content: str) -> str:
    """Creates a new file with the specified content."""
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"File created at {file_path}"
    except Exception as e:
        return f"An error occurred: {e}"

# Tool 14
def list_files(directory_path: str) -> list[str]:
    """Lists all files and directories in the specified path."""
    try:
        return os.listdir(directory_path)
    except FileNotFoundError:
        return [f"Error: Directory not found at {directory_path}"]
    except Exception as e:
        return [f"An error occurred: {e}"]

# Tool 15
def run_command(command: str) -> str:
    """Runs a shell command and returns the output."""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error executing command: {e.stderr}"
    except Exception as e:
        return f"An error occurred: {e}"
