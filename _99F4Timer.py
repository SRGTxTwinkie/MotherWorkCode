import time
import keyboard

minutes = input("How Long? (in minutes): ")
time.sleep(int(minutes) * 60)
keyboard.send("f4")
print("Done...")
