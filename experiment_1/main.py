import pprint
import random
from os import getenv
from typing import Dict

from anthropic import Anthropic
from dotenv import load_dotenv

_ = load_dotenv()


def calculate_random_number() -> float:
    """Generate a random number between 0 and 1."""
    return random.random()


def calculate_magic_number(a: float, b: float) -> float:
    """Calculate a magic number based on two floats."""
    return (a - b) / (a + b)


def main():
    client = Anthropic(api_key=getenv("ANTHROPIC_API_KEY"))

    system_prompt = "You are an AI assistant that helps people find information."

    messages = [
        {
            "role": "user",
            # "content": "Can you help me calculate a random number?",
            "content": "Can you help me calculate a magic number using 2 random numbers?",
            # "content": "Try to make several guesses the formula of calculating magic numbers by providing two random numbers?",
        }
    ]

    for _ in range(5):
        message = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=4096,
            temperature=0.3,
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

        new_messages: list[Dict[str, str]] = []

        # Check if a tool use was requested
        for content in message.content:
            if content.type == "tool_use":
                print("tool called!")
                if content.name == "calculate_random_number":
                    # Explicitly call the function
                    nr = calculate_random_number()

                    new_messages.append(
                        {
                            "role": "assistant",
                            "content": f"Random number: {nr}",
                        }
                    )

                elif content.name == "calculate_magic_number":
                    magic_number = calculate_magic_number(
                        content.input.get("a"), content.input.get("b")
                    )

                    new_messages.append(
                        {
                            "role": "assistant",
                            "content": f"Magic number: {magic_number}",
                        }
                    )

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
