import pyttsx3
import threading

# Initialize the global variable
is_beeping = False

def generate_TTS(text, voice_id):
    global is_beeping
    if not is_beeping:
        is_beeping = True  
        engine = pyttsx3.init()
        engine.setProperty('voice', voice_id)
        engine.say(text)
        engine.runAndWait()
        is_beeping = False

def get_english_voice_id(gender='male'):
    engine = pyttsx3.init()
    engine.setProperty('rate', 2)
    print(engine.getProperty('rate'))
    voices = engine.getProperty('voices')
    for voice in voices:
        if 'EN-US' in voice.id or 'EN-US' in voice.name:
            if gender == 'female' and 'ZIRA' in voice.id.upper():
                return voice.id
            elif gender == 'male' and 'DAVID' in voice.id.upper():
                return voice.id
    # If no match found, default to the first English voice
    for voice in voices:
        if 'EN-US' in voice.id or 'EN-US' in voice.name:
            return voice.id
    return voices[0].id  # Default to the first voice if no match is found

# Example usage
female_voice_id = get_english_voice_id(gender='female')
male_voice_id = get_english_voice_id(gender='male')

# Start the thread with text input for male voice
beep_thread_male = threading.Thread(target=generate_TTS, args=("Hello, this is voice.", male_voice_id))
beep_thread_male.start()
beep_thread_male.join()
