import os, base64
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()
client = OpenAI(base_url="https://api.meta.ai/v1", api_key=os.environ["MODEL_API_KEY"])

img = base64.b64encode(open("screen.png", "rb").read()).decode()
r = client.responses.create(
    model="sam-3.1",
    input=[{
        "role": "user",
        "content": [
            {"type": "input_text", "text": "Continue button"},
            {"type": "input_image", "image_url": "data:image/png;base64," + img},
        ],
    }],
)
print(r.output_text[:500])