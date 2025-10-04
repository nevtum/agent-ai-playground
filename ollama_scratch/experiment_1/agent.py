import logging
from collections.abc import Generator
from pathlib import Path

import ollama

from .response import OllamaStreamingResponse
from .tools import call_tool, tools

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
                    tool_call[0],
                    **tool_call[1],
                )
                self.conversation.append(
                    {
                        "role": "assistant",
                        "content": result,
                    }
                )
            except Exception as e:
                logger.error(f"Error calling tool {tool_call[0]}: {str(e)}")
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
            for raw_response in stream:
                response = OllamaStreamingResponse(raw_response)
                yield response.content()
                if response.has_tool_calls():
                    tool_calls.extend(response.tools_list())

            if tool_calls:
                self.execute_tool(tool_calls)
                continue

            break

        yield "\n"
