import RPi.GPIO as GPIO
import time
from datetime import datetime
from random import randint


class LED:

    def __init__(self, led):
        self.led = led
        self.off()
    
    def on(self):
        GPIO.output(self.led, True)

    def off(self):
        GPIO.output(self.led, False)

    def toggle(self):
        if GPIO.input(self.led):
            self.off()
        else: 
            self.on()

    def flash(self, count, sleep_time=0.5):
        for _ in range(count * 2):
            self.toggle()
            time.sleep(sleep_time)


class CountClicks:
    
    button = None
    default_state = True
    led = None
    count = 0

    def __init__(self, button, led=None):
        self.button = button
        self.led = LED(led) if led else self.led

    @property
    def button_state(self):
        return GPIO.input(self.button)

    @property
    def pressed(self):
        if self.button_state != self.default_state:
            self.count += 1
            return True

    def monitor(self):
        if self.pressed == True:
            self.led.on()
            time.sleep(0.2)
        else:
            self.led.off()


class Timer:
    def __init__(self, seconds):
        self.seconds = seconds
    
    def start(self):
        self.start_time = datetime.now()
    
    @property
    def expired(self):
        if (datetime.now() - self.start_time).total_seconds() >= self.seconds:
            return True
        else: 
            return False


if __name__ == "__main__":

    settings = {
        "a": {
            "button": 22,
            "led": 6,
        },
        "b": {
            "button": 27,
            "led": 19
        }
    }

    GPIO.setmode(GPIO.BCM)
    GPIO.cleanup()

    for key, value in settings.items():
        print(key, value)
        GPIO.setup(value["button"], GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(value["led"], GPIO.OUT)

    try:
        button_a = CountClicks(settings["a"]["button"], led=settings["a"]["led"])
        button_a = CountClicks(settings["b"]["button"], led=settings["b"]["led"])
        timer = Timer(5)

        flash_count = randint(1, 10)
        button_a.led.flash(flash_count, sleep_time=0.2)
        time.sleep(1)
        button_a.led.flash(3, sleep_time=0.05)


        timer.start()
        while True:
            button_a.monitor()
            
            if timer.expired:
                print("Times up!")
                break
        
        print(f"You pressed the button {button_a.count} out of {flash_count} times.")

        if button_a.count == flash_count:
            print("You win!")
        else:
            print("You loose, sucker.")
        

    except Exception as e:
        GPIO.cleanup()
        raise