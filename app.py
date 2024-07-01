import os
from dotenv import load_dotenv
import mysql.connector
from flask import Flask, request, jsonify
from flask_cors import CORS

load_dotenv()

mydb = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE")
)

cursor = mydb.cursor()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,PATCH,OPTIONS')
    return response

@app.route('/registrar', methods=['POST'])
def registrar_usuario():
    data = request.get_json()
    nombre = data['nombre']
    email = data['email']
    contraseña = data['contraseña']
    try:
        sql = "INSERT INTO usuarios (nombre, email, contraseña) VALUES (%s, %s, %s)"
        val = (nombre, email, contraseña)
        cursor.execute(sql, val)
        mydb.commit()
        return jsonify({"mensaje": "Usuario registrado correctamente"}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": f"Error al registrar usuario: {err}"}), 500

@app.route('/login', methods=['POST'])
def autenticar_usuario():
    data = request.get_json()
    email = data['email']
    contraseña = data['contraseña']
    try:
        sql = "SELECT * FROM usuarios WHERE email = %s AND contraseña = %s"
        cursor.execute(sql, (email, contraseña))
        resultado = cursor.fetchone()
        if resultado:
            return jsonify({"mensaje": "Inicio de sesión exitoso"}), 200
        else:
            return jsonify({"error": "Credenciales incorrectas"}), 401
    except mysql.connector.Error as err:
        return jsonify({"error": f"Error al autenticar usuario: {err}"}), 500

@app.route('/usuarios', methods=['GET'])
def obtener_usuarios():
    try:
        sql = "SELECT id, nombre, email FROM usuarios"
        cursor.execute(sql)
        usuarios = cursor.fetchall()
        usuarios_list = []
        for usuario in usuarios:
            usuario_dict = {
                "id": usuario[0],
                "nombre": usuario[1],
                "email": usuario[2]
            }
            usuarios_list.append(usuario_dict)
        return jsonify({"usuarios": usuarios_list}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": f"Error al obtener usuarios: {err}"}), 500

@app.route('/usuarios/<int:id>', methods=['DELETE'])
def eliminar_usuario(id):
    try:
        sql = "DELETE FROM usuarios WHERE id = %s"
        cursor.execute(sql, (id,))
        mydb.commit()
        return jsonify({"mensaje": f"Usuario con ID {id} eliminado correctamente"}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": f"Error al eliminar usuario: {err}"}), 500
    
@app.route('/usuarios/<int:id>', methods=['PATCH'])
def editar_usuario(id):
    try:
        data = request.get_json()
        
        if 'nombre' in data:
            cursor.execute("UPDATE usuarios SET nombre = %s WHERE id = %s", (data['nombre'], id))
        if 'email' in data:
            cursor.execute("UPDATE usuarios SET email = %s WHERE id = %s", (data['email'], id))
        if 'contraseña' in data:
            cursor.execute("UPDATE usuarios SET contraseña = %s WHERE id = %s", (data['contraseña'], id))
        
        mydb.commit()

        cursor.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
        usuario_actualizado = cursor.fetchone()
        return jsonify({"mensaje": "Usuario actualizado correctamente", "usuario": usuario_actualizado}), 200
    except mysql.connector.Error as err:
        return jsonify({"error": f"Error al actualizar usuario: {err}"}), 500



if __name__ == '__main__':
    app.run(debug=True, port=4000)
