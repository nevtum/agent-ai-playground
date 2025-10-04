from dotenv import load_dotenv
from os import getenv
from openai import OpenAI
from pathlib import Path
from .tools import call_tool, TOOLS

_ = load_dotenv()

MODEL: str = getenv("OPENAI_MODEL") or "gpt-4o-mini"

openai_client = OpenAI(api_key=getenv("OPENAI_API_KEY"))


def make_system_prompt(prompt: str) -> dict[str, str]:
    return {"role": "system", "content": prompt}


def make_user_prompt(prompt: str) -> dict[str, str]:
    return {"role": "user", "content": prompt}


class Agent:
    system_prompt: str = (Path(__file__).parent / "prompt.txt").read_text()

    def __init__(self, model: str = MODEL):
        self.model: str = model
        self.messages = [make_system_prompt(self.system_prompt)]

    def send_message(self, text: str):
        self.messages.append(make_user_prompt(text))

        response = openai_client.chat.completions.create(
            model=self.model,
            # tools=TOOLS,
            temperature=0.3,
            messages=self.messages,
        )

        result = response.choices[0].message.content
        return result

        # for item in response.output:
        #     if item.type == "function_call":
        #         if item.name == "get_horoscope":
        #             # 3. Execute the function logic for get_horoscope
        #             horoscope = get_horoscope(json.loads(item.arguments))

        #             # 4. Provide function call results to the model
        #             input_list.append({
        #                 "type": "function_call_output",
        #                 "call_id": item.call_id,
        #                 "output": json.dumps({
        #                   "horoscope": horoscope
        #                 })
        #             })
