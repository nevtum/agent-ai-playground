from .agent import Agent


def main():
    agent = Agent()
    print(agent.send_message("What are your skills?"))


if __name__ == "__main__":
    main()
