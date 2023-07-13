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
    use_default_speaker=False, filename="./file.wav"
)

# The language of the voice that speaks.
speech_config.speech_synthesis_voice_name = "en-GB-RyanNeural"

speech_synthesizer = speechsdk.SpeechSynthesizer(
    speech_config=speech_config, audio_config=audio_config
)

# Get text from the console and synthesize to the default speaker.
print("Enter some text that you want to speak >")
text = input()

speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()


if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print(f"Speech synthesized for text [{text}]")

    # Create an AudioDataStream instance from the result
    stream = speechsdk.AudioDataStream(speech_synthesis_result)

elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = speech_synthesis_result.cancellation_details
    print(f"Speech synthesis canceled: {cancellation_details.reason}")
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        if cancellation_details.error_details:
            print(f"Error details: {cancellation_details.error_details}")
            print("Did you set the speech resource key and region values?")
else:
    print("Speech synthesis failed")
