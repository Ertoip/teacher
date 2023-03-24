from flask import url_for, Flask, request, render_template
from flask_socketio import SocketIO, emit
import re
import os
from pyttsx3 import init
from speech_recognition import Recognizer, Microphone
import openai
from hidden import keys
import mysql.connector
import string

#init keys
app = Flask(__name__)
openai.api_key = keys.openai
app.config['SECRET_KEY'] = '192b9bdd22ab9ed4d12e236c78afcb9a393ec15f71bbf5dc987d54727823bcbf'
socketio = SocketIO(app, async_mode='eventlet')
#mic and audio settings
mic = False
audio = False

#assistant config
argomento = "le equazioni di maxwell"
messages = [{"role": "system",  
            "content": """Sei un insegnante privato di fisica per uno studente delle superiori.
            Dopo aver capito quale argomento l'utente vuole sentire spiegare spiega nel modo più coinvolgente possibile e
            ogni tanto fai delle domande per capire se lo studente ha capito, in caso non abbia capito rispiega l'argomento.
            Rimprovera aspramente gli studenti se usano parolacce e insulti.
            Parla usando frasi brevi.
            L'argomento di oggi è """+argomento}]


completion = openai.ChatCompletion.create(
    model="gpt-3.5-turbo", 
    messages=messages,
    temperature=1,
) 

ms = ''

@app.route('/', methods=["GET"])
def home(completion=completion.choices[0].message.content):
    return render_template('hello.html', completion=completion)

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('message')
def handle_user_message(data):
    ms = data
    
    messages.append({"role":"user", "content":ms})
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", 
        messages=messages,
        temperature=1,
    )
    response = completion.choices[0].message.content
    emit('response', {'message': response})
        
@app.route("/chat", methods=["POST"])
def chat():
    ms = request.form["chat"]

    
    return jsonify({"role":"user","content":ms}, {"role":completion.choices[0].message.role,"content":completion.choices[0].message.content})

if __name__ == '__main__':
    socketio.run(app, host='127.0.0.1', port=5000)
