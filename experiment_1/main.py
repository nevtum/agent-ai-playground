from pprint import pprint
from textwrap import dedent

from anthropic import Anthropic
from anthropic.types import MessageParam, ToolUseBlock

from .config import cfg
from .tools import handle_tool_call, TOOLS


def output_text(text: str):
    print(text)


def main():
    client = Anthropic(api_key=cfg.api_key)

    system_prompt = dedent("""
        You are an AI assistant that helps people calculate numbers. \
        Describe the plan how you will answer the question then \
        execute on that plan. Provide only the answer requested and \
        nothing else.
        """)

    user_prompt = "Can you help me calculate a magic number using a series of random numbers? Output the final calculation in <result></result>"
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
