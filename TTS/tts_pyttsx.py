# import pyttsx3

# def speak(text):
#     engine = pyttsx3.init()
#     engine.say(text)
#     engine.runAndWait()


# text = "안녕하세요. 반가워요."
# speak(text)

from espeak import espeak
import time

def speak():
    espeak.set_voice('english')
    espeak.synth("hello")
    while espeak.is_playing():
        time.sleep(5)

speak()