import speech_recognition as sr
import time

r = sr.Recognizer()
mic = sr.Microphone()

with mic as source:
    audio = r.listen(source)

out = r.recognize_google(audio)
print(out)

ap = ApplicationPuppet()
ap.start_app('photos')
ap.start_app('notes')

# Have pocketsphinx running nonstop
# Instances of VolumeChanger, Applications, StockTracker
# Chrome Search? Brightness? Youtube Search?
# Listen for keyword
#


