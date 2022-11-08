import RPi.GPIO as GPIO
from mfrc522 import SimpleMFRC522

class Rfid:
    
    def __init__(self):
        self.reader = SimpleMFRC522()
    
    def read_uid(self):
        try:
            uid = self.reader.read_id()
            return hex(uid).upper().strip("0X")
        
        finally:
            GPIO.cleanup()

