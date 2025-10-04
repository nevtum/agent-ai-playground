import random
from textwrap import dedent

from anthropic import Anthropic
from anthropic.types import MessageParam, ToolUseBlock

from .config import cfg


def calculate_random_number() -> float:
    """Generate a random number between 0 and 1."""
    return random.random()


def calculate_magic_number(a: float, b: float, c: float) -> float:
    """Calculate a magic number based on three floats."""
    return (a - b) / (a + b) + c


def handle_tool_call(content: ToolUseBlock) -> MessageParam:
    if content.name == "calculate_random_number":
        nr = calculate_random_number()
        return {
            "role": "assistant",
            "content": f"Random number: {nr}",
        }

    elif content.name == "calculate_magic_number":
        magic_number = calculate_magic_number(**content.input)
        return {
            "role": "assistant",
            "content": f"Magic number: {magic_number}",
        }

    raise ValueError(f"Unknown tool: {content.name}")


def main():
    client = Anthropic(api_key=cfg.api_key)

    system_prompt = dedent("""
        You are an AI assistant that helps people calculate numbers. \
        Describe the plan how you will answer the question then \
        execute on that plan. Provide only the answer requested and \
        nothing else.
        """)

    messages: list[MessageParam] = [
        {
            "role": "user",
            "content": "Can you help me calculate a magic number using a series of random numbers? Output the final calculation in <result></result>",
        }
    ]

    while True:
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
                    "description": "Calculates a magic number based on three floats",
                    "input_schema": {
                        "type": "object",
                        "properties": {
                            "a": {"type": "number"},
                            "b": {"type": "number"},
                            "c": {"type": "number"},
                        },
                        "required": ["a", "b", "c"],
                    },
                },
            ],
        )

        tool_calls: list[ToolUseBlock] = []

        for content in message.content:
            if content.type == "tool_use":
                tool_calls.append(content)
            elif content.type == "text":
                print(content.text)
                messages.append(
                    {
                        "role": "assistant",
                        "content": content.text,
                    }
                )

        if tool_calls:
            for content in tool_calls:
                try:
                    tool_response = handle_tool_call(content)
                    print(tool_response)
                    messages.append(tool_response)
                except ValueError as e:
                    print(f"Error handling tool call: {e}")
            continue

        break

    print("exited")


if __name__ == "__main__":
    main()
