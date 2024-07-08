import os
import wave
import json
import pyaudio
import requests
from vosk import Model, KaldiRecognizer
from gtts import gTTS
from pydub import AudioSegment
from pydub.playback import play

# Функция для загрузки модели Vosk
def download_model(url, model_path):
    if not os.path.exists(model_path):
        print(f"Загрузка модели с {url}...")
        r = requests.get(url, allow_redirects=True)
        with open(model_path, 'wb') as f:
            f.write(r.content)
        print("Модель загружена.")

# Загрузка модели Vosk, если она еще не скачана
model_dir = "model"
model_url = "https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip"
model_zip_path = os.path.join(model_dir, "vosk-model-small-ru-0.22.zip")
model_path = os.path.join(model_dir, "vosk-model-small-ru-0.22")

if not os.path.exists(model_path):
    os.makedirs(model_dir, exist_ok=True)
    download_model(model_url, model_zip_path)
    import zipfile
    with zipfile.ZipFile(model_zip_path, 'r') as zip_ref:
        zip_ref.extractall(model_dir)

def recognize_speech():
    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)

    p = pyaudio.PyAudio()
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
    stream.start_stream()

    print("Слушаю, говорите")

    try:
        while True:
            data = stream.read(4096, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                text = json.loads(result).get('text', '')

                if "привет я разработчик" in text:
                    respond("сегодня выходной")
                elif "я сегодня не приду домой" in text:
                    respond("Ну и катись отсюда")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()

def respond(text):
    tts = gTTS(text=text, lang='ru')
    tts.save("response.mp3")
    sound = AudioSegment.from_mp3("response.mp3")
    play(sound)
    os.remove("response.mp3")

if __name__ == "__main__":
    recognize_speech()
