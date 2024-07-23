import os

import assemblyai as aai
from dotenv import load_dotenv
load_dotenv()

aai.settings.api_key = os.getenv('ASSEMBLYAI_API_KEY')

TWILIO_SAMPLE_RATE = 8000 # Hz
final_transcript = []

def on_open(session_opened: aai.RealtimeSessionOpened):
    "Called when the connection has been established."
    print("Session ID:", session_opened.session_id)


def on_error(error: aai.RealtimeError):
    "Called when the connection has been closed."
    print("An error occured:", error)



class TwilioTranscriber(aai.RealtimeTranscriber):
    def __init__(self):
        super().__init__(
            on_data=self.on_data,
            on_error=on_error,
            on_open=on_open, # optional
            on_close=self.on_close, # optional
            sample_rate=TWILIO_SAMPLE_RATE,
            encoding=aai.AudioEncoding.pcm_mulaw
        )
        self.final_transcript = []


    def on_data(self, transcript: aai.RealtimeTranscript):
        "Called when a new transcript has been received."
        if not transcript.text:
            return
    
        if isinstance(transcript, aai.RealtimeFinalTranscript):
            self.final_transcript.append(transcript.text)
            print(transcript.text, end="\r\n")
        #else:
            #print(transcript.text, end="\r")

    def on_close(self):
        "Called when the connection has been closed."
        full_transcript = "".join(self.final_transcript)
        print("Final Transcript:", full_transcript)
        print("Closing Session")
