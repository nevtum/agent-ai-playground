import base64
from os import getenv
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

_ = load_dotenv()

MODEL: str = getenv("OPENAI_MODEL") or "gpt-4o-mini"

openai_client = OpenAI(api_key=getenv("OPENAI_API_KEY"))

system_message = """
You are an OCR assistant that extracts data points from \
charts. Extract all the data points accurately as it \
appears in the chart and output a list of (x, y) datapoints \
and other relevant data requested."""


def encode_image(filename: str) -> str:
    current_dir = Path(__file__).parent
    filepath = current_dir / filename

    with open(str(filepath), "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
        return encoded_string


def evaluate_image(filename: str):
    messages = [
        {"role": "system", "content": system_message},
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Extract title and data from this image: ",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/webp;base64,{encode_image(filename)}"
                    },
                },
            ],
        },
    ]
    response = openai_client.chat.completions.create(
        temperature=0.5, model=MODEL, max_tokens=3000, messages=messages
    )
    return response.choices[0].message.content


def main():
    result = evaluate_image("824bb15-134-86b2-d076-65cb1f7c0e7a.webp")
    print(result)


if __name__ == "__main__":
    main()
