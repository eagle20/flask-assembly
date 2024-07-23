import base64
import json
import os

from flask import Flask, request, Response
from flask_sock import Sock
from flask_sqlalchemy import SQLAlchemy
from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()

from twilio_transcriber import TwilioTranscriber

# Twilio authentication
account_sid = os.environ['TWILIO_ACCOUNT_SID']
api_key = os.environ['TWILIO_API_KEY_SID']
api_secret = os.environ['TWILIO_API_SECRET']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(api_key, api_secret, account_sid)
#client = Client(account_sid, auth_token)

# Twilio phone number to call
TWILIO_NUMBER = os.environ['TWILIO_NUMBER']

sqlalchemy_database_uri = os.environ['SQLALCHEMY_DATABASE_URI']

INCOMING_CALL_ROUTE = '/'
WEBSOCKET_ROUTE = '/realtime'

db = SQLAlchemy()

app = Flask(__name__)
sock = Sock(app)

app.config["SQLALCHEMY_DATABASE_URI"] = sqlalchemy_database_uri

db.init_app(app)

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
    transcriber = None
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
                print("Final Final 2:", transcriber.final_transcript)
                print('transcriber closed')
                
    

