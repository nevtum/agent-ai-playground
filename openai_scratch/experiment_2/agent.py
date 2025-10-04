from dotenv import load_dotenv
from os import getenv
from openai import OpenAI
from pathlib import Path

_ = load_dotenv()

MODEL: str = getenv("OPENAI_MODEL") or "gpt-4o-mini"

openai_client = OpenAI(api_key=getenv("OPENAI_API_KEY"))


class Agent:
    system_prompt: str = (Path(__file__).parent / "prompt.txt").read_text()

    def __init__(self, model: str = MODEL):
        self.model: str = model

    def send_message(self, text: str):
        response = openai_client.chat.completions.create(
            model=self.model,
            temperature=0.3,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {
                    "role": "user",
                    "content": text,
                },
            ],
        )

        result = response.choices[0].message.content
        return result
