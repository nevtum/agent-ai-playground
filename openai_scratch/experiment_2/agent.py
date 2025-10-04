import json
from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from openai.types.responses import ResponseFunctionToolCall

from .tools import TOOLS, call_tool

_ = load_dotenv()

MODEL: str = getenv("OPENAI_MODEL") or "gpt-4o-mini"

openai_client = OpenAI(api_key=getenv("OPENAI_API_KEY"))


def make_message(role: str, content: str) -> dict[str, str]:
    return {"role": role, "content": content}


def make_system_prompt(prompt: str) -> dict[str, str]:
    return make_message("system", prompt)


def make_user_prompt(prompt: str) -> dict[str, str]:
    return make_message("user", prompt)


class Agent:
    system_prompt: str = (Path(__file__).parent / "prompt.txt").read_text()

    def __init__(self, model: str = MODEL):
        self.model: str = model
        self.messages = [make_system_prompt(self.system_prompt)]

    def send_message(self, text: str):
        self.messages.append(make_user_prompt(text))

        while True:
            tool_calls: list[ResponseFunctionToolCall] = []
            reply: list[str] = []

            response = openai_client.responses.create(
                model=self.model,
                tools=TOOLS,
                temperature=0.3,
                input=self.messages,
            )

            for item in response.output:
                if item.type == "function_call":
                    tool_calls.append(item)
                elif item.type == "message":
                    for content in item.content:
                        reply.append(content.text)
                else:
                    raise Exception("Unexpected output type")

            if tool_calls:
                for tool in tool_calls:
                    self.messages.append(
                        {
                            "type": "function_call",
                            "call_id": tool.call_id,
                            "name": tool.name,
                            "arguments": tool.arguments,
                        }
                    )
                    result = call_tool(tool.name, **json.loads(tool.arguments))
                    self.messages.append(
                        {
                            "type": "function_call_output",
                            "call_id": tool.call_id,
                            "output": result,
                        }
                    )
                continue

            return "".join(reply)
