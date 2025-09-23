from os import getenv

from anthropic import Anthropic
from dotenv import load_dotenv

_ = load_dotenv()


def main():
    client = Anthropic(api_key=getenv("ANTHROPIC_API_KEY"))

    message = client.messages.create(
        max_tokens=1024,
        messages=[
            {
                "role": "user",
                "content": "Hello, Claude.",
            }
        ],
        model="claude-3-5-haiku-20241022",
    )
    print(message.content)


if __name__ == "__main__":
    main()
