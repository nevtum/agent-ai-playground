from pprint import pprint

from anthropic import Anthropic
from anthropic.types import MessageParam, ToolUseBlock

from .config import cfg
from .tools import TOOLS, handle_tool_call


def output_text(text: str):
    print(text)


system_prompt = """
You are an AI assistant that helps people calculate numbers. \
Describe the plan how you will answer the question then \
execute on that plan. Provide only the answer requested and \
nothing else.
"""

user_prompt = """
Calculate a magic number using a series of random numbers. \
In your final response, output only the calculation in json \
results similar to the following example:

{
    "result": 0.23626
}
"""


def main():
    client = Anthropic(api_key=cfg.api_key)

    output_text(user_prompt)

    messages: list[MessageParam] = [
        {
            "role": "user",
            "content": user_prompt,
        }
    ]

    while True:
        message = client.messages.create(
            model=cfg.model,
            max_tokens=cfg.max_tokens,
            temperature=cfg.temperature,
            system=system_prompt,
            messages=messages,
            tools=TOOLS,
        )

        tool_calls: list[ToolUseBlock] = []

        for content in message.content:
            if content.type == "tool_use":
                tool_calls.append(content)
                messages.append(
                    {
                        "role": "assistant",
                        "content": [
                            {
                                "type": "tool_use",
                                "id": content.id,
                                "name": content.name,
                                "input": content.input,
                            }
                        ],
                    }
                )
            elif content.type == "text":
                output_text(content.text)
                messages.append(
                    {
                        "role": "assistant",
                        "content": content.text,
                    }
                )

        if tool_calls:
            for content in tool_calls:
                tool_response = handle_tool_call(content.name, **content.input)
                output_text(tool_response)
                messages.append(
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "tool_result",
                                "tool_use_id": content.id,
                                "content": tool_response,
                            }
                        ],
                    }
                )
            continue

        break

    pprint(messages)


if __name__ == "__main__":
    main()
