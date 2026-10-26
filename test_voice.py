import asyncio, base64, json, os, wave
import websockets

URL = "ws://localhost:4000/v1/realtime?model=muse-voice-transcribe&intent=transcription"
HEADERS = {"Authorization": "Bearer " + os.environ["LITELLM_API_KEY"]}

def pcm_chunks(path, chunk_ms=100):
    with wave.open(path) as w:
        rate, frames = w.getframerate(), w.readframes(w.getnframes())
    step = rate * 2 * chunk_ms // 1000
    return rate, [frames[i:i + step] for i in range(0, len(frames), step)]

async def main():
    rate, chunks = pcm_chunks("question.wav")
    async with websockets.connect(URL, additional_headers=HEADERS) as ws:
        print(json.loads(await ws.recv())["type"])
        await ws.send(json.dumps({
            "type": "session.update",
            "session": {"type": "transcription", "audio": {"input": {
                "format": {"type": "audio/pcm", "rate": rate},
                "transcription": {"model": "meta/muse-voice-transcribe-1.0"},
                "turn_detection": None,
            }}},
        }))
        print(json.loads(await ws.recv())["type"])
        for chunk in chunks:
            await ws.send(json.dumps({"type": "input_audio_buffer.append", "audio": base64.b64encode(chunk).decode()}))
            await asyncio.sleep(0.1)
        await ws.send(json.dumps({"type": "input_audio_buffer.commit"}))
        try:
            while True:
                e = json.loads(await ws.recv())
                if e["type"] == "conversation.item.input_audio_transcription.completed":
                    print("YOU SAID:", e["transcript"])
        except websockets.exceptions.ConnectionClosedOK:
            pass

asyncio.run(main())