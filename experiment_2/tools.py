import subprocess
from textwrap import dedent

from .permissions import human_gate


@human_gate
def call_system_command(command: str) -> str:
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        return dedent(f"""
        Error: {result.stderr.strip()}
        """)
    return result.stdout.strip()


def call_tool(name, **kwargs) -> str:
    if name == call_system_command.__name__:
        return call_system_command(command=kwargs["command"])
    else:
        raise ValueError(f"Unknown tool: {name}")


tools = [
    {
        "type": "function",
        "function": {
            "name": "call_system_command",
            "description": "Executes a specified Linux command in the system shell.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The name of the linux command to execute.",
                    },
                },
                "required": ["command"],
            },
        },
    }
]
