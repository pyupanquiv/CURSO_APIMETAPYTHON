from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client
import json

app = Flask(__name__)

# Configuración de la base de datos SQLITE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de la tabla log
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_y_hora = db.Column(db.DateTime, default=datetime.utcnow)
    texto = db.Column(db.TEXT)

# Crear la tabla si no existe
with app.app_context():
    db.create_all()

# Función para ordenar los registros por fecha y hora
def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: x.fecha_y_hora, reverse=True)

@app.route('/')
def index():
    # Obtener todos los registros de la base de datos
    registros = Log.query.all()
    registros_ordenados = ordenar_por_fecha_y_hora(registros)
    return render_template('index.html', registros=registros_ordenados)

# Token de verificación para la configuración 
TOKEN_ANDERCODE = 'ANDERCODE'

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        challenge = verificar_token(request)
        return challenge
    elif request.method == 'POST':
        response = recibir_mensajes(request)
        return response

def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')

    if challenge and token == TOKEN_ANDERCODE:
        return challenge
    else:
        return jsonify({'error': 'Token Invalido'}), 401

def recibir_mensajes(req):
    try:
            req = request.get_json()
            entry = req['entry'][0]
            changes = entry['changes'][0]
            value = changes['value']
            objeto_mensaje = value['messages']

            if objeto_mensaje:
                 messages = objeto_mensaje[0]

                 if "type" in messages:
                      tipo = messages["type"]

                      if tipo == "interactive":
                           return 0
                      if "text" in messages:
                           text = messages["text"]["body"]
                           numero = messages["from"]
                           
                           enviar_mensajes_whatsapp(text,numero)


            return jsonify({'message': 'EVENT_RECEIVED'})
    except Exception as e:
                return jsonify({'message': 'EVENT_RECEIVED'})

def enviar_mensajes_whatsapp(texto,number):
    texto = texto.lower()

    if "hola" in texto:
         data={
                "messaging_product": "whatsapp",    
                "recipient_type": "individual",
                "to": number,
                "type": "text",
                "text": {
                    "preview_url": false,
                    "body": "Hello Paul Como Estas"
             }
        }
    else:
         data={
                "messaging_product": "whatsapp",    
                "recipient_type": "individual",
                "to": number,
                "type": "text",
                "text": {
                    "preview_url": false,
                    "body": "Hola, visita mi web Paul Yupanqui"
             }
        }
    #Convetir en diccionario a formato JSON
    data = json.dumps(data)

    headers = {
         "Content-Type" : "application/json",
         "Authorization" : "Bearer EAARPO5ZBdXIEBO9TWECMEEtLMxQBGucUAtk7lCniJp3UKnzQc7AaoqxZCD5Xs1nRawqZABp2rfEGUvMgG7IaiGRaVgXsky34tQl9e92wUSSMwzrB7zrmDMp3WXSwGcVb9lqPbZB1ZC1NJDe9ExWEg7vu0KTmXIEtgVbGvXIUZA9rHBhAg9nhHZBdU4qiokZCSqJ8bbR7kCE93CfqXkTcHrUvACuYvv565xs5wWJLH2FGSNoZD"
    }

    connection = http.client.HTTPSConnection("graph.facebook.com")

    try:
        connection.request("POST","/v20.0/360639233803052/messages", data, headers) 
        response = connection.getresponse()
        print(response.status, response.reason)
    except Exception as e:
        agregar_mensajes_log(json.dumps(e))
    finally:
         connection.close()


    req_data = req.get_json()  # Asegúrate de obtener JSON correctamente

    if not req_data:
        return jsonify({'error': 'Invalid JSON'}), 400

    mensaje_texto = json.dumps(req_data, indent=2)  # Convierte el JSON a texto para guardar en la base de datos
    agregar_mensajes_log(mensaje_texto)  # Almacenar el mensaje en el log
    




    return jsonify({'message': 'EVENT_RECEIVED'})

# Función para agregar mensajes y guardar en la base de datos
def agregar_mensajes_log(texto):
    # Guardar el mensaje en la base de datos
    nuevo_registro = Log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
