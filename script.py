import array
import threading
import pyaudio
import simpleaudio as sa
import speech_recognition as sr
import sys
import _thread
import time
import wave

p = pyaudio.PyAudio()
r = sr.Recognizer()

CHUNK = 1024
THRESHOLD = 500
CHANNELS = 2
RATE = 44100
FORMAT = pyaudio.paInt16
WAVE_OUTPUT_FILENAME = "output.wav"

def is_silent():
    stream = p.open(format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK)

    data = stream.read(CHUNK, exception_on_overflow=False)

    stream.stop_stream()
    stream.close()

    as_ints = array.array('h', data)
    max_value = max(as_ints)
    if max_value < THRESHOLD:
        return True
    else:
        return False

def record_audio_to_file():
    print("\033[1;33;49m Listening...")

    stream = p.open(format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK)

    frames = []
    while is_silent() == False:
        for i in range(0, int(RATE / CHUNK)):
            data = stream.read(CHUNK)
            frames.append(data)

    stream.stop_stream()
    stream.close()

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def play_confused_response():
    print("huh")

def play_audio(file):
    wf = wave.open(file, 'rb')

    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
        channels=wf.getnchannels(),
        rate=wf.getframerate(),
        output=True)

    data = wf.readframes(CHUNK)

    while data != b'':
        stream.write(data)
        data = wf.readframes(CHUNK)

    stream.stop_stream()
    stream.close()
    wf.close()

def translate_audio_to_text():
    print("\033[1;33;49m Processing...")

    with sr.AudioFile(WAVE_OUTPUT_FILENAME) as source:
        audio = r.record(source)

    try:
        text = r.recognize_google(audio)
        print("\033[1;37;49m Keywords said : ", text.split())
        return text
    except sr.UnknownValueError:
        play_confused_response()
        print("\033[1;31;49m Unable to identify the audio")
        return ""

def search_file_for_text(file, text):
    with open(file) as f:
        if text != "":
            lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line in text:
                    print("\033[1;32;49m Found :", line.split(), "in response")
                    return True

def handle_input(text):
    if search_file_for_text('input/intro.txt', text):
        play_audio("responses/hi_hello.wav")
    elif search_file_for_text('input/questions.txt', text):
        print("questions")
    elif search_file_for_text('input/uncertain.txt', text):
        print("uncertain")

while True:
    if is_silent() == False:
        record_audio_to_file()
        text = translate_audio_to_text()
        handle_input(text)
