import subprocess
from textwrap import dedent

from .permissions import human_gate


@human_gate
def call_system_command(command: str) -> str:
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            return dedent(f"Error: {result.stderr.strip()}")
        return result.stdout.strip()
    except Exception as ex:
        return f"Failed to call system command: {ex}"


def call_tool(name, **kwargs) -> str:
    if name == call_system_command.__name__:
        return call_system_command(**kwargs)
    else:
        return f"Unknown tool: {name}"


TOOLS = [
    {
        "type": "function",
        "name": "call_system_command",
        "description": "Executes a system command in the shell and returns the output or error message.",
        "parameters": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The system command to execute.",
                }
            },
            "required": ["command"],
            "additionalProperties": False,
        },
        "strict": True,
    }
]
