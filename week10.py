from openai import OpenAI
import os

client = OpenAI(api_key="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")

messages = [
    {"role": "system", "content": "You are a helpful Python assistant."},
    {"role": "user", "content": "Write an explanation of API for beginners."}
]

response = client.chat.completions.create(
    model = "gpt-4.1-mini",
    messages = messages
)

print(response.choices[0].message.content)