import RPi.GPIO as GPIO
import time
from datetime import datetime
import random
from collections import Counter


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
            return True
        else:
            self.led.off()
            return False


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


def create_flash_pattern(total_flash_count, buttons_count):
    flashes = []

    last_random_button = random.randint(0, buttons_count)
    for _ in range(total_flash_count):
        if total_flash_count > 0:
            possible_random_button = [n for n in range(buttons_count) if n != last_random_button]
            random_button = random.choice(possible_random_button)
            random_flash_count = random.randint(1, total_flash_count)
            for _ in range (random_flash_count):
                flashes.append(random_button)
            # flashes.append(
            #     (random_button, random_flash_count)
            # )
            total_flash_count -= random_flash_count
            last_random_button = random_button

    print('Flashes:', flashes)
    return flashes



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
        # Create button objects
        buttons = [
            CountClicks(settings["a"]["button"], led=settings["a"]["led"]),
            CountClicks(settings["b"]["button"], led=settings["b"]["led"]),
        ]
        buttons_count = len(buttons)
    
        # Get game details
        count = 8
        flashes = create_flash_pattern(count, buttons_count)

        # Lets play!
        for button in flashes:
            buttons[button].led.flash(1, sleep_time=0.2)

        time.sleep(0.5)
        buttons[1].led.flash(3, sleep_time=0.05)  # TODO replace with seperate LED

        # Accept input
        timer = Timer(10)
        timer.start()

        input_history = []
        while True:
            for button_number, button in enumerate(buttons):
                if button.monitor():
                    input_history.append(button_number)
            
            if timer.expired:
                print("Times up!")
                break

        print('\nYou win:', input_history == flashes)
            
        print('Expected input:', input_history)    
        print('Your input:    ', flashes)

    except Exception as e:
        GPIO.cleanup()
        raise 