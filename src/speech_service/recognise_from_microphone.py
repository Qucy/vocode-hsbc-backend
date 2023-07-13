"""Recognise from microphone"""
import os

import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv()

os.environ["SPEECH_KEY"] = os.getenv("AZURE_SPEECH_KEY")
os.environ["SPEECH_REGION"] = os.getenv("AZURE_SPEECH_REGION")


def recognize_from_microphone():
    """docstring!"""
    # This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
    speech_config = speechsdk.SpeechConfig(
        subscription=os.environ.get("SPEECH_KEY"),
        region=os.environ.get("SPEECH_REGION"),
    )
    speech_config.speech_recognition_language = "en-US"

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)
    speech_recognizer = speechsdk.SpeechRecognizer(
        speech_config=speech_config, audio_config=audio_config
    )

    print("Speak into your microphone.")
    speech_recognition_result = speech_recognizer.recognize_once_async().get()

    if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print(f"Recognized: {(speech_recognition_result.text)}")
    elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
        print(
            f"No speech could be recognized: {speech_recognition_result.no_match_details}"
        )
    elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = speech_recognition_result.cancellation_details
        print(f"Speech Recognition canceled: {cancellation_details.reason}")
        if cancellation_details.reason == speechsdk.CancellationReason.Error:
            print(f"Error details: {cancellation_details.error_details}")
            print("Did you set the speech resource key and region values?")


recognize_from_microphone()