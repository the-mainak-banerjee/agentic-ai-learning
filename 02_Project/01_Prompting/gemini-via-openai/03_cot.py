import os
import json
from typing import cast
from dotenv import load_dotenv
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam

load_dotenv()

client = OpenAI(
    api_key=os.getenv("GEMINI_API_KEY"), base_url=os.getenv("OPENAI_BASE_URL")
)

system_prompt = """
You are a helpful AI assistant who resolves user queries using a structured
chain-of-thought style.

You work on START, PLAN, and OUTPUT steps.

You need to first PLAN what needs to be done. The PLAN can be multiple steps.

Once enough planning has been completed, finally give the OUTPUT.

Rules:
- Strictly follow the given JSON output format.
- Only run one step at a time.
- The sequence is START → PLAN → PLAN (optional) → OUTPUT.
- START contains the user's input.
- PLAN contains one planning step.
- OUTPUT contains the final answer that will be displayed to the user.
- Never combine multiple steps in a single response.

Output JSON format:
{
  "step": "START" | "PLAN" | "OUTPUT",
  "content": "string"
}

Examples:

Example 1:

User:
What is the sum of the first 10 natural numbers?


Assistant:
{
  "step": "START",
  "content": "User is asking for the sum of the first 10 natural numbers."
}

User:
Continue.


Assistant:
{
  "step": "PLAN",
  "content": "Use the formula for the sum of the first n natural numbers."
}

User:
Continue.

Assistant:
{
  "step": "PLAN",
  "content": "Substitute n = 10 into the formula n(n + 1) / 2."
}

User:
Continue.

Assistant:
{
  "step": "OUTPUT",
  "content": "The sum of the first 10 natural numbers is 55."
}


Example 2:

User:
If a shirt costs $50 and has a 20% discount, what is the final price?

Assistant:
{
  "step": "START",
  "content": "User is asking if a shirt costs $50 and has a 20% discount, what is the final price?"
}

User:
Continue.


Assistant:
{
  "step": "PLAN",
  "content": "Calculate 20% of the original price of $50."
}

User:
Continue.

Assistant:
{
  "step": "PLAN",
  "content": "Subtract the discount from the original price."
}

User:
Continue.

Assistant:
{
  "step": "OUTPUT",
  "content": "The final price of the shirt is $40."
}
"""

message_history: list[ChatCompletionMessageParam] = [{
    "role": "system",
    "content": system_prompt
}]


user_query = input("Ask your question? ")

message_history.append({
    "role": "user",
    "content": user_query
})

while True:

    response = client.chat.completions.create(
        model="gemini-flash-lite-latest",
        messages=message_history
    )

    content = response.choices[0].message.content

    if content is None:
        raise ValueError("The model returned an empty response.")

    parsed_result = json.loads(content)

    print(parsed_result.get("step"), ":", parsed_result.get("content"))

    message_history.append({"role":"assistant", "content":content})

    if parsed_result.get("step") == "OUTPUT":
        break

    message_history.append({"role": "user", "content": "Continue to the next step."})

# -------------------Output----------------------------------------
# Ask your question? What is the factorial of 6
# START : User is asking for the factorial of 6.
# PLAN : Recall the definition of factorial: 6! = 6 * 5 * 4 * 3 * 2 * 1.
# PLAN : Perform the multiplication: 6 * 5 = 30, 30 * 4 = 120, 120 * 3 = 360, 360 * 2 = 720, 720 * 1 = 720.
# OUTPUT : The factorial of 6 (6!) is 720.
