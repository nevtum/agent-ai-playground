from pathlib import Path
import ollama

from .tools import call_tool, tools
import logging

logging.basicConfig()


def main():
    messages = [
        {
            "role": "system",
            "content": (Path(__file__).parent / "prompt.txt").read_text(),
        },
        {
            "role": "user",
            "content": "describe each file in this directory?",
        },
    ]
    MODEL = "llama3.2"

    for response in ollama.chat(
        model=MODEL,
        tools=tools,
        messages=messages,
        stream=True,
    ):
        if "tool_calls" in response["message"]:
            for tool_call in response["message"]["tool_calls"]:
                result = call_tool(
                    tool_call["function"]["name"],
                    **tool_call["function"]["arguments"],
                )
                messages.append(
                    {
                        "role": "assistant",
                        "content": result,
                    }
                )

    for response in ollama.chat(
        model=MODEL,
        tools=tools,
        messages=messages,
        stream=True,
    ):
        if "tool_calls" in response["message"]:
            raise ValueError("not expected!")
        print(response["message"]["content"], end="", flush=True)

    print("\n\nfinished\n")


if __name__ == "__main__":
    main()
