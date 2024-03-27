import pyttsx3

def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

text = "안녕하세요. 반가워요."
speak(text)
