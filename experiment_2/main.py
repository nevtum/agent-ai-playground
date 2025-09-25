import ollama


def main():
    messages = [
        {
            "role": "user",
            "content": "Describe some of the business applications of Generative AI",
        }
    ]
    MODEL = "llama3.2"

    response = ollama.chat(model=MODEL, messages=messages)
    print(response["message"]["content"])


if __name__ == "__main__":
    main()
