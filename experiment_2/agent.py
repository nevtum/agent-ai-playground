from collections.abc import Generator
from pathlib import Path
from .tools import tools, call_tool
import ollama
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def make_system_prompt(prompt: str) -> dict[str, str]:
    return {"role": "system", "content": prompt}


def make_user_prompt(prompt: str) -> dict[str, str]:
    return {"role": "user", "content": prompt}


system_prompt = make_system_prompt((Path(__file__).parent / "prompt.txt").read_text())


class Agent:
    def __init__(self, model):
        self.model = model
        self.conversation = []

    def execute_tool(self, tool_calls):
        for tool_call in tool_calls:
            try:
                result = call_tool(
                    tool_call["function"]["name"],
                    **tool_call["function"]["arguments"],
                )
                self.conversation.append(
                    {
                        "role": "assistant",
                        "content": result,
                    }
                )
            except Exception as e:
                logger.error(
                    f"Error calling tool {tool_call['function']['name']}: {str(e)}"
                )
                self.conversation.append(
                    {
                        "role": "assistant",
                        "content": f"Error: {str(e)}",
                    }
                )

    def send_message(self, message: str) -> Generator[str, None, None]:
        self.conversation.append(make_user_prompt(message))

        while True:
            tool_calls = []

            stream = ollama.chat(
                model=self.model,
                tools=tools,
                messages=self.conversation,
                stream=True,
            )
            for response in stream:
                if "tool_calls" in response["message"]:
                    tool_calls = response["message"]["tool_calls"]
                else:
                    yield response["message"]["content"]

            if not tool_calls:
                break

            self.execute_tool(tool_calls)

        yield "\n"
