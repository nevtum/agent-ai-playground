import logging
from pathlib import Path

import ollama

from .response import OllamaStreamingResponse
from .tools import call_tool, tools

logging.basicConfig()


def get_question() -> str:
    # return "describe each file in this directory"
    return input("User: ")


def main():
    messages = [
        {
            "role": "system",
            "content": (Path(__file__).parent / "prompt.txt").read_text(),
        },
    ]
    MODEL = "llama3.2"

    while True:
        messages.append(
            {
                "role": "user",
                "content": get_question(),
            }
        )

        while True:
            tool_results = []

            for raw_response in ollama.chat(
                model=MODEL,
                tools=tools,
                messages=messages,
                stream=True,
            ):
                response = OllamaStreamingResponse(raw_response)

                print(response.content(), end="", flush=True)

                if response.has_tool_calls():
                    for tool_name, tool_args in response.tools_list():
                        result = call_tool(tool_name, **tool_args)
                        tool_results.append(result)

            if not tool_results:
                break
            else:
                for result in tool_results:
                    messages.append(
                        {
                            "role": "assistant",
                            "content": result,
                        }
                    )

        print("")

    print("\n\nfinished\n")


if __name__ == "__main__":
    main()
