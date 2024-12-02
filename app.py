import base64
import json
import os
import pywav

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

class SupaUser(db.Model):
    date = db.Column(db.DateTime, primary_key=True)
    transcript = db.Column(db.String)
    session_id = db.Column(db.String)
    call_id = db.Column(db.String)
    payload = db.Column(db.String)

with app.app_context():
    db.create_all()

pcmu_data = bytearray()
file_path = "/var/data/"
#-----------------------------------------------

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
    pcmu_data.clear()
    print('called')
    #payload_append = ""
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
                c_id = data['start']['callSid']
                s_id = data['start']['streamSid']
                output_filename = s_id + ".wav"
            case "media":
                payload_b64 = data['media']['payload']
                #payload_append = payload_append + payload_b64
                payload_mulaw = base64.b64decode(payload_b64)
                pcmu_data.extend(payload_mulaw)
                transcriber.stream(payload_mulaw)
            case "stop":
                print('twilio stopped')
                transcriber.close()
                #-------------------
                filname = file_path + output_filename
                wave_write = pywav.WavWrite(filname, 1, 8000, 8, 7)
                wave_write.write(pcmu_data)
                wave_write.close()
                #--------------------
                data = SupaUser(date=transcriber.created, transcript=transcriber.final_transcript, session_id = s_id, call_id = c_id, payload = filname)
                db.session.add(data)
                db.session.commit()
                print("Len:", len(pcmu_data))
                print("file:", filname)
                print("Final Final 2:", transcriber.final_transcript)
                #print("Date:", transcriber.created)
                print('transcriber closed')
                break
                
    if __name__ == "__main__":
        app.run(port=PORT, debug=DEBUG)

