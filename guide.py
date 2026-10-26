import os, re, json, base64
from dotenv import load_dotenv
from openai import OpenAI
from PIL import Image, ImageDraw

load_dotenv()
client = OpenAI(base_url="https://api.meta.ai/v1", api_key=os.environ["MODEL_API_KEY"])

GOAL = "I want to log in to Instagram"
LANGUAGE = "English"

with open("screen.png", "rb") as f:
    data_url = "data:image/png;base64," + base64.b64encode(f.read()).decode()

# 1. Muse Spark decides the next step
prompt = (
    f'User goal: "{GOAL}". Look at the screen and give ONE next step for an older adult. '
    f'Reply only with JSON: {{"instruction": "one short sentence in {LANGUAGE}", '
    f'"target": "short English description of the button or field to use"}}'
)
r = client.chat.completions.create(
    model="muse-spark-1.2",
    messages=[{"role": "user", "content": [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": {"url": data_url}},
    ]}],
)
data = json.loads(re.search(r"\{.*\}", r.choices[0].message.content, re.S).group(0))
print("SAY:", data["instruction"])
print("TARGET:", data["target"])

# 2. SAM 3.1 finds the target
s = client.responses.create(model="sam-3.1", input=[{"role": "user", "content": [
    {"type": "input_text", "text": data["target"]},
    {"type": "input_image", "image_url": data_url},
]}])
m = re.search(r"<\|box;x1=([\d.]+);y1=([\d.]+);x2=([\d.]+);y2=([\d.]+)", s.output_text)
if not m:
    print("No box found")
    raise SystemExit
x1, y1, x2, y2 = map(float, m.groups())

# 3. Draw the highlight
im = Image.open("screen.png").convert("RGB")
ImageDraw.Draw(im).rectangle([x1, y1, x2, y2], outline=(255, 215, 0), width=8)
im.save("result.png")
print("Saved result.png")