from textwrap import dedent
from .permissions import human_gate


@human_gate
def call_system_command(command: str) -> str:
    return dedent("""
    -rw-r--r--@  1 root  staff     134  1 Jun 16:21 .zprofile
    -rw-------@  1 root  staff   71793 30 Sep 20:31 .zsh_history
    -rw-r--r--@  1 root  staff    4018 12 Jun 18:24 .zshrc
    drwxr-xr-x   3 root  staff      96  9 Jun 11:00 Applications
    drwx------+  8 root  staff     256 20 Sep 17:17 Desktop
    drwx------+  7 root  staff     224 16 Aug 17:43 Documents
    drwx------+ 15 root  staff     480 14 Sep 12:33 Downloads
    drwxr-xr-x@  3 root  staff      96  3 Jun 14:08 go
    drwx------@ 93 root  staff    2976 24 Sep 19:59 Library
    drwx------   3 root  staff      96 23 May 09:05 Movies
    drwx------+  4 root  staff     128 23 May 09:27 Music
    drwx------+  4 root  staff     128 23 May 09:05 Pictures
    drwxr-xr-x+  4 root  staff     128 23 May 09:05 Public
    """)


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
