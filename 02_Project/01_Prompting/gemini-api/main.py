from dotenv import load_dotenv
from google import genai

load_dotenv()  

client = genai.Client()

interaction = client.interactions.create(
    model="gemini-flash-lite-latest",
    input="Hey, explain prompt enginnering in simple word."
)


print(interaction.output_text)