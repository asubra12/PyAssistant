import os
from pocketsphinx import pocketsphinx, get_model_path
from sphinxbase import sphinxbase
import pyaudio
import speech_recognition as sr


def start_keyphrase_recognition(keyphrase_function, key_phrase):
    """ Starts a thread that is always listening for a specific key phrase. Once the
        key phrase is recognized, the thread will call the keyphrase_function. This
        function is called within the thread (a new thread is not started), so the
        key phrase detection is paused until the function returns.
    :param keyphrase_function: function that is called when the phrase is recognized
    :param key_phrase: a string for the key phrase
    """
    modeldir = get_model_path()
    datadir = "pocketsphinx/test/data"

    # Create a decoder with certain model
    config = pocketsphinx.Decoder.default_config()
    # Use the mobile voice model (en-us-ptm) for performance constrained systems
    config.set_string('-hmm', os.path.join(modeldir, 'en-us'))
    config.set_string('-lm', os.path.join(modeldir, 'en-us.lm.bin'))
    config.set_string('-dict', os.path.join(modeldir, 'cmudict-en-us.dict'))
    config.set_string('-keyphrase', key_phrase)
    config.set_string('-logfn', 'files/sphinx.log')
    config.set_float('-kws_threshold', 1)

    # Start a pyaudio instance
    p = pyaudio.PyAudio()
    # Create an input stream with pyaudio
    stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
    # Start the stream
    stream.start_stream()

    # Process audio chunk by chunk. On keyword detected perform action and restart search
    decoder = pocketsphinx.Decoder()
    decoder.start_utt()
    # Loop forever
    while True:
        # Read 1024 samples from the buffer
        buf = stream.read(1024)
        # If data in the buffer, process using the sphinx decoder
        if buf:
            decoder.process_raw(buf, False, False)
        else:
            break
        # If the hypothesis is not none, the key phrase was recognized
        if decoder.hyp() is not None:
            keyphrase_function()
            # Stop and reinitialize the decoder
            decoder.end_utt()
            decoder.start_utt()


def example_function():
    """ Dummy function that prints a notification when the key phrase is recognized.
    """
    print("Keyword detected!")


def capture_speech():
    r = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        audio = r.listen(source)

    out = r.recognize_google(audio)
    print(out)
    return


if __name__ == "__main__":
    # Start key phrase recognition and call the "demo_function" when triggered
    start_keyphrase_recognition(capture_speech, "Mercury")


# Have pocketsphinx running nonstop
# Instances of VolumeChanger, Applications, StockTracker
# Chrome Search? Brightness? Youtube Search?
# Listen for keyword
#

