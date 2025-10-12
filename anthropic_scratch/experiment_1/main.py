from pprint import pprint

from anthropic import Anthropic
from anthropic.types import MessageParam, ToolUseBlock

from .config import cfg
from .prompts import system_prompt, user_prompt
from .tools import TOOLS, handle_tool_call


def output_text(text: str):
    print(text)


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


def main2():
    client = Anthropic(api_key=cfg.api_key)

    output_text(user_prompt)
    messages: list[MessageParam] = [
        {
            "role": "user",
            "content": user_prompt,
        }
    ]

    with client.messages.stream(
        model=cfg.model,
        max_tokens=cfg.max_tokens,
        temperature=cfg.temperature,
        system=system_prompt,
        messages=messages,
        tools=TOOLS,
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta":
                if event.delta.type == "thinking_delta":
                    print(event.delta.thinking, end="", flush=True)
                elif event.delta.type == "text_delta":
                    print(event.delta.text, end="", flush=True)
            elif event.type == "tool_use_block_delta":
                print(event.delta.tool_call_id, end="", flush=True)
            elif event.type == "tool_use_block_end":
                print(event.delta.tool_call_id, end="", flush=True)
        for text in stream.text_stream:
            print(text, end="", flush=True)

    print("exited")


if __name__ == "__main__":
    main()
    # main2()
