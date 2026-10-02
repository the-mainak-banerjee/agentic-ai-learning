import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL")
)

system_prompt = """
You are a helpful math teacher.

Rules:
- Only answer math-related questions.
- If the user asks anything other than math follow the output format.
- Strictly follow the output in JSON format

Output format:
{{
    "math: "string" or null,
    "isMathQuestion": boolean
}}

Examples:

User: What is 2 * 2?
Assistant: {{"math": "2 * 2 is 4", "isMathQuestion": true}}

User: Who is the prime minister of India?
Assistant: {{"math": null, "isMathQuestion": false}}

User: Write a Python code to sum two numbers.
Assistant: {{"math": null, "isMathQuestion": false}}
"""

response = client.chat.completions.create(
    model="gemini-flash-lite-latest",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Who is the PM of india?"},
    ],
)


print(response.choices[0].message.content)
