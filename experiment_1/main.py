from dotenv import load_dotenv
from os import getenv

load_dotenv()


def main():
    print(getenv("API_KEY"))


if __name__ == "__main__":
    main()
