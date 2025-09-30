from .agent import Agent
import logging

logging.basicConfig()


def main():
    MODEL = "llama3.2"

    agent = Agent(MODEL)

    for chunk in agent.send_message("describe each file in this directory?"):
        print(chunk, end="", flush=True)

    while True:
        question = input("\nUser: ")

        if question == "":
            continue

        if question in ["exit", "quit"]:
            break

        for chunk in agent.send_message(question):
            print(chunk, end="", flush=True)

    print("\nfinished")


if __name__ == "__main__":
    main()
