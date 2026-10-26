import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url="https://api.meta.ai/v1", api_key=os.environ["MODEL_API_KEY"])
r = client.chat.completions.create(
    model="muse-spark-1.2",
    messages=[{"role": "user", "content": "Say hello in Hindi."}],
)
print(r.choices[0].message.content)