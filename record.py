import sounddevice as sd
from scipy.io import wavfile

rate = 16000
print("Speak now for 5 seconds...")
audio = sd.rec(int(5 * rate), samplerate=rate, channels=1, dtype="int16")
sd.wait()
wavfile.write("question.wav", rate, audio)
print("Saved question.wav")