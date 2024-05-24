from gtts import gTTS
import playsound as ps
import pygame

text = "hello"
tts = gTTS(text= text, lang='ko')
tts.save("./hello.mp3")
ps.playsound("./hello.mp3")