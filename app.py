from flask import Flask
from flask_sock import Sock

INCOMING_CALL_ROUTE = '/'
WEBSOCKET_ROUTE = '/realtime'

app = Flask(__name__)
sock = Sock(app)


@app.route(INCOMING_CALL_ROUTE)
def receive_call():
    return "Real time phone call transcription app"

@sock.route(WEBSOCKET_ROUTE)
def transcription_websocket(ws):
    pass
    
def hello_world():
    return 'Hello, World!'
