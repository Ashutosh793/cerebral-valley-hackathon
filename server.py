import os, re, json, base64
from dotenv import load_dotenv
from openai import OpenAI
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
client = OpenAI(base_url="https://api.meta.ai/v1", api_key=os.environ["MODEL_API_KEY"])

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/guide")
def guide(frame: UploadFile = File(...), goal: str = Form(...), language: str = Form("English")):
    raw = frame.file.read()
    data_url = "data:image/jpeg;base64," + base64.b64encode(raw).decode()

    prompt = (
        f'User goal: "{goal}". Look at the screen and give ONE next step for an older adult. '
        f'Reply only with JSON: {{"instruction": "one short sentence in {language}", '
        f'"target": "short English description of the button or field to use"}}'
    )
    r = client.chat.completions.create(
        model="muse-spark-1.2",
        messages=[{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": data_url}},
        ]}],
    )
    try:
        data = json.loads(re.search(r"\{.*\}", r.choices[0].message.content, re.S).group(0))
    except Exception:
        return {"instruction": "Sorry, I could not see the screen clearly. Please hold the phone steady.", "target": None, "box": None}

    s = client.responses.create(model="sam-3.1", input=[{"role": "user", "content": [
        {"type": "input_text", "text": data["target"]},
        {"type": "input_image", "image_url": data_url},
    ]}])
    m = re.search(r"<\|box;x1=([\d.]+);y1=([\d.]+);x2=([\d.]+);y2=([\d.]+);w=([\d.]+);h=([\d.]+)", s.output_text)
    box = None
    if m:
        x1, y1, x2, y2, w, h = map(float, m.groups())
        box = [x1 / w, y1 / h, x2 / w, y2 / h]  # 0 to 1, so any screen size works

    return {"instruction": data["instruction"], "target": data["target"], "box": box}

from fastapi.responses import FileResponse

@app.get("/")
def index():
    return FileResponse("index.html")