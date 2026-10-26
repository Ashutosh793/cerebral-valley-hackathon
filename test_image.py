import os, base64
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url="https://api.meta.ai/v1", api_key=os.environ["MODEL_API_KEY"])

img = base64.b64encode(open("screen.png", "rb").read()).decode()
r = client.chat.completions.create(
    model="muse-spark-1.2",
    messages=[{
        "role": "user",
        "content": [
            {"type": "text", "text": "I want to log in. Which button should I press? Reply with the button name and where it is on the screen, in one sentence."},
            {"type": "image_url", "image_url": {"url": "data:image/png;base64," + img}},
        ],
    }],
)
print(r.choices[0].message.content)