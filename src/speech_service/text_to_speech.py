"""Text to speech"""
import os

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()

os.environ["SPEECH_KEY"] = os.getenv("AZURE_SPEECH_KEY")
os.environ["SPEECH_REGION"] = os.getenv("AZURE_SPEECH_REGION")

# This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
speech_config = speechsdk.SpeechConfig(
    subscription=os.environ.get("SPEECH_KEY"), region=os.environ.get("SPEECH_REGION")
)
audio_config = speechsdk.audio.AudioOutputConfig(
    use_default_speaker=True  # , filename="./file.wav"
)

# The language of the voice that speaks.
speech_config.speech_synthesis_voice_name = "en-GB-RyanNeural"

speech_synthesizer = speechsdk.SpeechSynthesizer(
    speech_config=speech_config, audio_config=audio_config
)

# Get text from the console and synthesize to the default speaker.
text = """
Thank you, Martin. So just a Q1 recap. Model Y became the best-selling vehicle of any
kind in Europe and the best-selling non-pickup vehicle in the United States.
And this is in spite of a lot of challenges in production and delivery, so it's
a huge credit to the Tesla team for achieving these great results. The -- it is
worth pointing out that the current macro environment remains uncertain. I
don't think I'm telling anyone anything people don't already know, especially
with large purchases such as cars.
"""

speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

print(f"Speech synthesized for text [{text}]")

# Create an AudioDataStream instance from the result
audio_data_stream = speechsdk.AudioDataStream(speech_synthesis_result)
audio_buffer = bytes(16000)
filled_size = audio_data_stream.read_data(audio_buffer)
while filled_size > 0:
    print("{} bytes received.".format(filled_size))
    filled_size = audio_data_stream.read_data(audio_buffer)

    if speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_synthesis_result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            if cancellation_details.error_details:
                print(f"Error details: {cancellation_details.error_details}")
                print("Did you set the speech resource key and region values?")
