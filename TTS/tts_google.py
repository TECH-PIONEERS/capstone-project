from gtts import gTTS
import os
from tempfile import NamedTemporaryFile

def speak(text):
    tts = gTTS(text=text, lang='ko')  # 텍스트를 한국어로 음성 변환
    with NamedTemporaryFile(delete=False) as f:  # 임시 파일 생성
        tts.write_to_fp(f)  # 음성을 임시 파일에 저장
        f.close()  # 파일 닫기
    os.system("mpg321 - < " + f.name)  # 임시 파일을 바로 재생 (Linux 예시)
    os.unlink(f.name)  # 임시 파일 삭제

text = "안녕하세요. 반가워요."
speak(text)
