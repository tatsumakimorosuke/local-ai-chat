
import json
from urllib.request import Request, urlopen

# 会話履歴を保存するリスト
messages = [
    {
        "role": "system",
        "content": "あなたは日本語のAIアシスタントです。必ず日本語で回答してください。"
    }
]

while True:
    prompt = input("\nAIへの質問 > ")

    if prompt.lower() == "exit":
        print("終了します。")
        break

    # ユーザーの発言を履歴に追加
    messages.append({
        "role": "user",
        "content": prompt
    })

    data = {
        "model": "qwen3:4b",
        "messages": messages,
        "stream": False
    }

    req = Request(
        "http://localhost:11434/api/chat",
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )

    with urlopen(req, timeout=240) as response:
        result = json.load(response)

    answer = result["message"]["content"]

    print("\nAI:", answer)

    # AIの回答も履歴に追加
    messages.append({
        "role": "assistant",
        "content": answer
    })
