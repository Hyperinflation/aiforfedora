"""
CLI entrypoint for local Qwen assistant.
"""

from agent import LocalAssistantAgent
from config import Settings


def run_cli() -> None:
    settings = Settings()
    agent = LocalAssistantAgent(settings)

    print("Local Qwen Assistant baslatildi.")
    print("Cikis icin: exit veya quit")
    print("-" * 50)

    while True:
        try:
            user_input = input("Sen> ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nCikis yapildi.")
            break

        if user_input.lower() in {"exit", "quit"}:
            print("Gorusmek uzere.")
            break
        if not user_input:
            continue

        response = agent.handle(user_input)
        print(f"Asistan> {response}\n")


if __name__ == "__main__":
    run_cli()

