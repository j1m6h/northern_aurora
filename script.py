import array
import pyaudio
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

stream = p.open(format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    frames_per_buffer=CHUNK)

def is_silent():
    data = stream.read(CHUNK)
    as_ints = array.array('h', data)
    max_value = max(as_ints)
    if max_value < THRESHOLD:
        return True
    else:
        return False

def record_audio_to_file():
    print("Recording...")
    frames = []
    while is_silent() == False:
        for i in range(0, int(RATE / CHUNK)):
            data = stream.read(CHUNK)
            frames.append(data)

    print("Finished recording")

    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def play_confused_response():
    print("huh")

def translate_audio_to_text():
    with sr.AudioFile(WAVE_OUTPUT_FILENAME) as source:
        audio = r.record(source)

    try:
        text = r.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        play_confused_response()
        print("Unable to identify the audio")
        return ""

def handle_input(text):
    it = 0
    with open('input/intro.txt') as file:
        if text != "":
            _list = text.split()
            lines = file.readlines()
            for word in _list:
                for line in lines:
                    line = line.strip()
                    if word == line:
                        it += 1
    
    # if 2 or more key phrases were found
    if it >= 2:
        print("Success")

def exit():
    stream.close_stream()
    stream.close()
    p.terminate()

while True:
    if is_silent() == False:
        record_audio_to_file()
        text = translate_audio_to_text()
        handle_input(text)