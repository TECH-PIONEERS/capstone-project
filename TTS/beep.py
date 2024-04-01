import threading
import pygame
import time

def generate_alert_beep():
    generate_long_beep()
    generate_high_beep()
    generate_high_beep()
    generate_high_beep()

def generate_long_beep():
    pygame.init()
    pygame.mixer.init()
    beep_sound = pygame.mixer.Sound("sound/long_beep.wav")
    beep_sound.play()
    time.sleep(2)
    
def generate_high_beep():
    pygame.init()
    pygame.mixer.init()
    beep_sound = pygame.mixer.Sound("sound/high_beep.wav")
    beep_sound.play()
    time.sleep(1)

def generate_low_beep():
    pygame.init()
    pygame.mixer.init()
    beep_sound = pygame.mixer.Sound("sound/low_beep.wav")
    beep_sound.play()
    time.sleep(1)

def main():
    while True:
        user_input = input("Action: ")
        if user_input == 'alert':
            # 공위 범위 밖으로
            beep_thread = threading.Thread(target=generate_alert_beep)
            beep_thread.start()
            print("Running high beep")
        if user_input == 'high':
            # 정렬 성공
            beep_thread = threading.Thread(target=generate_high_beep)
            beep_thread.start()
            print("Running high beep")
        if user_input == 'low':
            # 정렬 실패
            beep_thread = threading.Thread(target=generate_low_beep)
            beep_thread.start()
            print("Running low beep")
        if user_input == 'test':
            # 쓰레드 테스트
            print("test")
    
if __name__ == "__main__":
    main()
