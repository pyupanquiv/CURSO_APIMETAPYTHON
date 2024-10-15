from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
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

                           agregar_mensajes_log(json.dumps(text))
                           agregar_mensajes_log(json.dumps(numero))


            return jsonify({'message': 'EVENT_RECEIVED'})
    except Exception as e:
                return jsonify({'message': 'EVENT_RECEIVED'})



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
