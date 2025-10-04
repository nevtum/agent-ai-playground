from anthropic import Anthropic
from anthropic.types import MessageParam

from .config import cfg
from .prompts import system_prompt, user_prompt
from .tools import TOOLS


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
