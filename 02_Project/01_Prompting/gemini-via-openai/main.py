import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)


response = client.chat.completions.create(
    model="gemini-flash-lite-latest",
    messages=[
        {"role": "user", "content": "Hey  explain prompt enginnering in simple word."}
    ],
)

print(response.choices)
print("-" * 35)
print(response.choices[0].message.content)
