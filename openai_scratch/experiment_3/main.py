from os import getenv

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

_ = load_dotenv()

MODEL: str = getenv("OPENAI_MODEL") or "gpt-4o-mini"

openai_client = OpenAI(api_key=getenv("OPENAI_API_KEY"))

system_message = "You are a helpful assistant that responds in markdown"


def stream_response(prompt: str):
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": prompt},
    ]
    stream = openai_client.chat.completions.create(
        model=MODEL, messages=messages, stream=True
    )
    result = ""
    for chunk in stream:
        result += chunk.choices[0].delta.content or ""
        yield result


def main():
    view = gr.Interface(
        fn=stream_response,
        inputs=[gr.Textbox(label="Your message:", lines=10)],
        outputs=[gr.Markdown(label="Response:")],
        flagging_mode="never",
    )
    view.launch()


if __name__ == "__main__":
    main()
