from os import getenv

import gradio as gr
from dotenv import load_dotenv
from openai import OpenAI

from .prompts import DEFAULT_PROMPT_KEY, PROMPTS

_ = load_dotenv()

MODEL: str = getenv("OPENAI_MODEL") or "gpt-4o-mini"

openai_client = OpenAI(api_key=getenv("OPENAI_API_KEY"))


class PromptChatUI:
    def __init__(self):
        self.current_prompt_key = DEFAULT_PROMPT_KEY
        self.model = MODEL
        self.client = openai_client

    def _current_system(self) -> str:
        return PROMPTS.get(self.current_prompt_key, PROMPTS[DEFAULT_PROMPT_KEY])

    def set_prompt_key(self, key: str) -> str:
        self.current_prompt_key = key
        return PROMPTS.get(key, PROMPTS[DEFAULT_PROMPT_KEY])

    def to_messages(self, history) -> list[dict[str, str]]:
        messages = []
        for user_msg, assistant_msg in history:
            messages.append({"role": "user", "content": user_msg})
            messages.append({"role": "assistant", "content": assistant_msg})
        return messages

    def chat(self, message: str, history: list[list[str]]):
        system = self._current_system()
        messages = [{"role": "system", "content": system}]
        messages.extend(self.to_messages(history))
        messages.append({"role": "user", "content": message})

        stream = self.client.chat.completions.create(
            model=self.model, messages=messages, stream=True
        )
        result = ""
        for chunk in stream:
            content = chunk.choices[0].delta.content or ""
            result += content
            yield result


def main():
    ui = PromptChatUI()

    # Build a Blocks UI with a dropdown to select the system prompt and a live preview
    with gr.Blocks() as demo:
        gr.Markdown("# Chat with adjustable system prompt (Dropdown)")

        with gr.Row():
            prompt_dropdown = gr.Dropdown(
                label="System prompt presets",
                choices=list(PROMPTS.keys()),
                value=DEFAULT_PROMPT_KEY,
            )
            prompt_preview = gr.Markdown(PROMPTS[DEFAULT_PROMPT_KEY])

        with gr.Row():
            gr.ChatInterface(fn=ui.chat)

        # Wire up interactions
        # Update the instance state; the chat function will always read from the instance
        prompt_dropdown.change(
            ui.set_prompt_key, inputs=[prompt_dropdown], outputs=[prompt_preview]
        )

    demo.launch()


if __name__ == "__main__":
    main()
