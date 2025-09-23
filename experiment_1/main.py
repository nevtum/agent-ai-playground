import pprint
import random

from anthropic import Anthropic
from anthropic.types import MessageParam, ToolUseBlock

from .config import cfg


def calculate_random_number() -> float:
    """Generate a random number between 0 and 1."""
    return random.random()


def calculate_magic_number(a: float, b: float) -> float:
    """Calculate a magic number based on two floats."""
    return (a - b) / (a + b)


def handle_tool_call(content: ToolUseBlock) -> MessageParam:
    if content.name == "calculate_random_number":
        nr = calculate_random_number()
        return {
            "role": "assistant",
            "content": f"Random number: {nr}",
        }

    elif content.name == "calculate_magic_number":
        magic_number = calculate_magic_number(
            content.input.get("a"), content.input.get("b")
        )
        return {
            "role": "assistant",
            "content": f"Magic number: {magic_number}",
        }

    raise ValueError(f"Unknown tool: {content.name}")


def main():
    client = Anthropic(api_key=cfg.api_key)

    system_prompt = "You are an AI assistant that helps people perform tasks."

    messages: list[MessageParam] = [
        {
            "role": "user",
            "content": "Can you help me calculate a magic number using 2 random numbers?",
        }
    ]

    for _ in range(5):
        message = client.messages.create(
            model=cfg.model,
            max_tokens=cfg.max_tokens,
            temperature=cfg.temperature,
            system=system_prompt,
            messages=messages,
            tools=[
                {
                    "name": "calculate_random_number",
                    "description": "Calculates a random number between 0 and 1",
                    "input_schema": {
                        "type": "object",
                        "properties": {},
                        "required": [],
                    },
                },
                {
                    "name": "calculate_magic_number",
                    "description": "Calculates a magic number based on two floats",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "a": {"type": "number"},
                            "b": {"type": "number"},
                        },
                        "required": ["a", "b"],
                    },
                },
            ],
        )

        new_messages: list[MessageParam] = []

        for content in message.content:
            if content.type == "tool_use":
                try:
                    tool_response = handle_tool_call(content)
                    new_messages.append(tool_response)
                except ValueError as e:
                    print(f"Error handling tool call: {e}")

            elif content.type == "text":
                new_messages.append(
                    {
                        "role": "assistant",
                        "content": content.text,
                    }
                )

        pprint.pprint(new_messages)
        messages.extend(new_messages)

    print("exited")


if __name__ == "__main__":
    main()
