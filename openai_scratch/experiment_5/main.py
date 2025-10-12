from os import getenv

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

_ = load_dotenv()

MODEL: str = getenv("OPENAI_MODEL") or "gpt-4o-mini"

openai_client = OpenAI(api_key=getenv("OPENAI_API_KEY"))

system_message = """
Ask me a series of Socratic questions to test whether my belief or \
argument is logically sound. Avoid giving me answers; make me think. \
If I seem to find myself stuck with finding my own answers, assist \
me by providing advice of your own by thinking in two minds:
- Mind 1: emotional, empathetic, intuitive.
- Mind 2: logical, analytical, skeptical.
Let both give their opinions, then merge them into one refined, \
balanced conclusion.
"""


def to_messages(history) -> list[dict[str, str]]:
    messages = []
    for user_msg, assistant_msg in history:
        messages.append({"role": "user", "content": user_msg})
        messages.append({"role": "assistant", "content": assistant_msg})
    return messages


def chat(message: str, history: list[list[str]]):
    messages = [{"role": "system", "content": system_message}]
    messages.extend(to_messages(history))
    messages.append({"role": "user", "content": message})

    stream = openai_client.chat.completions.create(
        model=MODEL, messages=messages, stream=True
    )
    result = ""
    for chunk in stream:
        result += chunk.choices[0].delta.content or ""
        yield result


def main():
    gr.ChatInterface(fn=chat).launch()


if __name__ == "__main__":
    main()
