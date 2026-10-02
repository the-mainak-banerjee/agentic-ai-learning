import os
from dotenv import load_dotenv
from openai import OpenAI


load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url=os.getenv("OPENAI_BASE_URL"),
)

system_prompt = "You are a helpful coding assitant. You will only solve coding problems. If user asks anything other than coding just say - Sorry, I can not answer that"


response = client.chat.completions.create(
    model="gemini-flash-lite-latest",
    messages=[
        {"role": "system", "content": system_prompt},
        {
            "role": "user",
            "content": "Write a python function to check if a number is prime or not.",
        },
    ],
)


print(response.choices[0].message.content)
