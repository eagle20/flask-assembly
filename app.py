import base64
import json
import os

from flask import Flask, request, Response
from flask_sock import Sock
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()

from twilio_transcriber import TwilioTranscriber

# Twilio authentication
account_sid = os.environ['TWILIO_ACCOUNT_SID']
api_key = os.environ['TWILIO_API_KEY_SID']
api_secret = os.environ['TWILIO_API_SECRET']
client = Client(api_key, api_secret, account_sid)

# Twilio phone number to call
TWILIO_NUMBER = os.environ['TWILIO_NUMBER']

INCOMING_CALL_ROUTE = '/'
WEBSOCKET_ROUTE = '/realtime'

# Try calling bubble on call completion
call = client.calls.create(
    status_callback="https://joenair12.bubbleapps.io/version-test/api/1.1/wf/twilio/initialize",
    status_callback_event=["completed"],
    status_callback_method="POST",
    to=TWILIO_NUMBER,
    from_="+13106581962",
)

app = Flask(__name__)
sock = Sock(app)


@app.route(INCOMING_CALL_ROUTE, methods=['GET', 'POST'])
def receive_call():
    if request.method == 'POST':
        xml = f"""
<Response>
    <Say>
        Speak to see your speech transcribed in the console
    </Say>
    <Connect>
        <Stream url='wss://{request.host}{WEBSOCKET_ROUTE}' />
    </Connect>
</Response>
""".strip()
        return Response(xml, mimetype='text/xml')
    else:
        return f"Real time phone call transcription app"

@sock.route(WEBSOCKET_ROUTE)
def transcription_websocket(ws):
    print('called')
    while True:
        data = json.loads(ws.receive())
        match data['event']:
            case "connected":
                transcriber = TwilioTranscriber()
                transcriber.connect()
                print('transcriber connected')
            case "start":
                print('twilio started')
            case "media":
                payload_b64 = data['media']['payload']
                payload_mulaw = base64.b64decode(payload_b64)
                transcriber.stream(payload_mulaw)
            case "stop":
                print('twilio stopped')
                transcriber.close()
                print('transcriber closed')
    

