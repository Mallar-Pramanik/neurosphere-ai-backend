import ollama

response = ollama.chat(
    model="qwen3:1.7b",
    messages=[
        {"role": "user", "content": "Hello, who are you?"}
    ]
)

print(response["message"]["content"])