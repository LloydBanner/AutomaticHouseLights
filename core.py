import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
#pir
GPIO.setup(40, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(22, GPIO.IN, pull_up_down=GPIO.PUD_UP)
#LED
GPIO.setup(15, GPIO.OUT)

class room:
    
    def __init__(self, detectors, lights):
        self.people = 0
        self.state = 'normal'
        self.detectors = detectors
        self.lights = lights
        
    def inc_people(self):
        print('incrementing')
        self.people += 1
        self.update()
        
    def dec_people(self):
        print('decrementing')
        if self.people != 0:
            self.people -= 1
        self.update()
                
    def lights_off(self):
        for light in self.lights:
            GPIO.output(light, False)
            
    def lights_on(self):
        for light in self.lights:
            GPIO.output(light, true)
            
    def detect(self):
        for detector in self.detectors:
            activity = detector.detect()
            if activity == 'in':
                self.inc_people()
            elif activity == 'out':
                self.dec_people()
                
    def update(self):
        if self.people > 0 and self.state == 'normal':
            for light in self.lights:
                GPIO.output(light, True)
        else:
            for light in self.lights:
                GPIO.output(light, False)
            

class detector:
    
    def __init__(self, sensor_in, sensor_out):
        self.sensor_in = sensor_in
        self.sensor_out = sensor_out
        self.old_time = time.time()
        self.new_time = time.time()
        self.delta = 0
        
    def detect_in(self):
        return GPIO.input(self.sensor_in)
    
    def detect_out(self):
        return GPIO.input(self.sensor_out)
    
    def delta_update(self):
        self.old_time = self.new_time
        self.new_time = time.time()
        self.delta = self.new_time - self.old_time
    
    def detect(self):
        if self.detect_in():
            timer = 2
            print('going_in')
            while timer > 0:
                print('waiting')
                timer -= self.delta
                self.delta_update()
                if self.detect_in():
                    print('in')
                    return 'in'
        elif self.detect_out():
            timer = 2
            print('going_out')
            while timer > 0:
                print('waiting')
                timer -= self.delta
                self.delta_update()
                if self.detect_out():
                    print('out')
                    return 'out'
        else:
            return False

my_door = detector(22, 40)
my_room = room([my_door], [15])
my_room.update()

running = True
old_time = time.time()
new_time = time.time()
delta = 0

def delta_update():
    global old_time
    global new_time
    global delta
    old_time = new_time
    new_time = time.time()
    delta = (new_time - old_time)

def enter(channel):
    GPIO.remove_event_detect(22)
    GPIO.remove_event_detect(40)
    print('entering')
    global delta
    GPIO.add_event_detect(22, GPIO.FALLING, callback=entered, bouncetime=300)
    timer = 2
    while timer > 0:
        delta_update()
        timer -= delta
    GPIO.remove_event_detect(22)
    GPIO.add_event_detect(40, GPIO.FALLING, callback=enter, bouncetime=300)
    GPIO.add_event_detect(22, GPIO.FALLING, callback=exit, bouncetime=300)
    
def entered(channel):
    GPIO.remove_event_detect(22)
    print('entered')
    my_room.inc_people()
    GPIO.add_event_detect(40, GPIO.FALLING, callback=enter, bouncetime=300)
    GPIO.add_event_detect(22, GPIO.FALLING, callback=exit, bouncetime=300)
    
def exit(channel):
    GPIO.remove_event_detect(40)
    GPIO.remove_event_detect(22)
    print('exiting')
    global delta
    GPIO.add_event_detect(40, GPIO.FALLING, callback=exited, bouncetime=300)
    timer = 2
    while timer > 0:
        delta_update()
        timer -= delta
    GPIO.remove_event_detect(40)
    GPIO.add_event_detect(40, GPIO.FALLING, callback=enter, bouncetime=300)
    GPIO.add_event_detect(22, GPIO.FALLING, callback=exit, bouncetime=300)
    
def exited(channel):
    GPIO.remove_event_detect(40)
    print('exited')
    my_room.dec_people()
    GPIO.add_event_detect(40, GPIO.FALLING, callback=enter, bouncetime=300)
    GPIO.add_event_detect(22, GPIO.FALLING, callback=exit, bouncetime=300)

out_time = time.time()
in_time = time.time()
activated = False

def outgoing(channel):
    global out_time
    global activated
    out_time = time.time()
    if activated:
        check()
    else:
        activated = True
        
def ingoing(channel):
    global in_time
    global activated
    in_time = time.time()
    if activated:
        check()
    else:
        activated = True
    
def check():
    global activated
    global in_time
    global out_time
    print(in_time - out_time)
    if abs(in_time - out_time) < 2:
        if in_time - out_time < 0:
            my_room.dec_people()
        else:
            my_room.inc_people()
    activated = False
        
    
GPIO.add_event_detect(40, GPIO.RISING, callback=outgoing, bouncetime=300)
GPIO.add_event_detect(22, GPIO.RISING, callback=ingoing, bouncetime=300)  
    
try:
    while True:
        if activated:
            now = time.time()
            if abs(now - out_time) > 3:
                if abs(now - in_time) > 3:
                    activated = False
except KeyboardInterrupt:
    GPIO.cleanup()
    

##    
##in_room = False;
##on = True
##timer = 0
##
##while _running:
##    delta()
##    if timer > 0:
##        timer -= _delta
##    else:
##        if GPIO.input(40) and not in_room:
##            in_room = True
##            timer = 4
##        elif GPIO.input(40) and in_room:
##            in_room = False
##            timer = 4
##    if in_room and on:
##        GPIO.output(15, True)
##    else:
##        GPIO.output(15, False)
##    print(in_room)
        