from agent import LocalAssistantAgent
from config import Settings

tests = [
    "sudo apt install kodu ne işe yarar.",
    "Merhaba ben Semih.",
    "Terminalimde EOF kodu çalıştır.",
    "En güncel Fedora sürümü nedir?",
]

agent = LocalAssistantAgent(Settings())

for i, t in enumerate(tests, 1):
    print(f"\n--- TEST {i} ---")
    print("USER:", t)
    print("ASSISTANT:", agent.handle(t))