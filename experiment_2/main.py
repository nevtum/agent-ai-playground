from pathlib import Path
import ollama

from .tools import call_tool, tools
import logging

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
                        tool_results.append(result)
                else:
                    print(response["message"]["content"], end="", flush=True)

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
