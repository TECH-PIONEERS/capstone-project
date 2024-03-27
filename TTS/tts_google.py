# pip install gTTS

from gtts import gTTS
import os
from tempfile import TemporaryFile

def speak(text):
    tts = gTTS(text=text, lang='ko')  # 텍스트를 한국어로 음성 변환
    f = TemporaryFile()  # 임시 파일 생성
    tts.write_to_fp(f)  # 음성을 임시 파일에 저장
    f.seek(0)  # 파일의 처음으로 이동
    os.system("mpg321 - < " + f.name)  # 임시 파일을 바로 재생 (Linux 예시)

text = "안녕하세요. 반가워요."
speak(text)
