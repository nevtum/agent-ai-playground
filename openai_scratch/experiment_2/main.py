import logging

from .agent import Agent

logging.basicConfig()


def main():
    agent = Agent()

    while True:
        question = input("User: ")
        response = agent.send_message(question)
        print(response)

    print("finished")


if __name__ == "__main__":
    main()
