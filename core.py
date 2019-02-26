import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
#pir
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#LED
GPIO.setup(15, GPIO.OUT)

_running = True
_old_time = 0
_new_time = time.time()
_delta = 0.1

def delta():
    global _old_time
    global _new_time
    global _delta
    _old_time = _new_time
    _new_time = time.time()
    _delta = (_new_time - _old_time)
    
in_room = False;
on = True
timer = 0

while _running:
    delta()
    if timer > 0:
        timer -= _delta
    else:
        if GPIO.input(22) and not in_room:
            in_room = True
            timer = 4
        elif GPIO.input(22) and in_room:
            in_room = False
            timer = 4
    if in_room and on:
        GPIO.output(15, True)
    else:
        GPIO.output(15, False)
    print(in_room)
        