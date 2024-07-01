from flask import Flask, request, jsonify
import mysql.connector
from datetime import timedelta

app = Flask(__name__)

# Configuración de la base de datos
db_config = {
    'user': 'root',
    'password': 'AaNl0019',  # Reemplaza 'tu_contraseña' con tu contraseña de MySQL
    'host': 'localhost',
    'database': 'sistema_turnos'
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

def timedelta_to_str(timedelta_obj):
    if isinstance(timedelta_obj, timedelta):
        total_seconds = int(timedelta_obj.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"
    return timedelta_obj

@app.route('/turnos', methods=['GET'])
def get_turnos():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM turnos')
    turnos = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # Convertir los objetos timedelta a cadenas
    for turno in turnos:
        turno['hora_inicio'] = str(turno['hora_inicio'])
        turno['hora_fin'] = str(turno['hora_fin'])
    
    return jsonify(turnos)

@app.route('/turnos', methods=['POST'])
def add_turno():
    new_turno = request.json
    nombre_cliente = new_turno['nombre_cliente']
    fecha = new_turno['fecha']
    hora_inicio = new_turno['hora_inicio']
    hora_fin = new_turno['hora_fin']
    estado = new_turno['estado']

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar si ya existe un turno con la misma hora y fecha
    cursor.execute('''
        SELECT * FROM turnos
        WHERE fecha = %s AND (
            (hora_inicio <= %s AND hora_fin > %s) OR
            (hora_inicio < %s AND hora_fin >= %s)
        )
    ''', (fecha, hora_fin, hora_inicio, hora_inicio, hora_fin))
    existing_turno = cursor.fetchone()

    if existing_turno:
        cursor.close()
        conn.close()
        return jsonify({"error": "Ya existe un turno en ese horario para la misma fecha."}), 400

    # Si no existe conflicto, insertar el nuevo turno
    cursor.execute('''
        INSERT INTO turnos (nombre_cliente, fecha, hora_inicio, hora_fin, estado)
        VALUES (%s, %s, %s, %s, %s)
    ''', (nombre_cliente, fecha, hora_inicio, hora_fin, estado))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify(new_turno), 201

@app.route('/turnos/<int:id>', methods=['PUT'])
def update_turno(id):
    update_turno = request.json
    nombre_cliente = update_turno['nombre_cliente']
    fecha = update_turno['fecha']
    hora_inicio = update_turno['hora_inicio']
    hora_fin = update_turno['hora_fin']
    estado = update_turno['estado']

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE turnos
        SET nombre_cliente = %s, fecha = %s, hora_inicio = %s, hora_fin = %s, estado = %s
        WHERE id = %s
    ''', (nombre_cliente, fecha, hora_inicio, hora_fin, estado, id))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify(update_turno)

@app.route('/turnos/<int:id>', methods=['PATCH'])
def patch_turno(id):
    patch_data = request.json

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Obtener los valores actuales del turno
    cursor.execute('SELECT * FROM turnos WHERE id = %s', (id,))
    turno = cursor.fetchone()

    if not turno:
        return jsonify({"error": "Turno no encontrado"}), 404

    # Actualizar solo los campos proporcionados en la solicitud
    turno.update(patch_data)

    cursor.execute('''
        UPDATE turnos
        SET nombre_cliente = %s, fecha = %s, hora_inicio = %s, hora_fin = %s, estado = %s
        WHERE id = %s
    ''', (turno['nombre_cliente'], turno['fecha'], turno['hora_inicio'], turno['hora_fin'], turno['estado'], id))
    conn.commit()
    cursor.close()
    conn.close()
    
    # Convertir los objetos timedelta a cadenas
    turno['hora_inicio'] = str(turno['hora_inicio'])
    turno['hora_fin'] = str(turno['hora_fin'])
    
    return jsonify(turno)

@app.route('/turnos/<int:id>', methods=['DELETE'])
def delete_turno(id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM turnos WHERE id = %s', (id,))
    conn.commit()
    cursor.close()
    conn.close()
    return '', 204

if __name__ == '__main__':
    app.run(port=5000, debug=True)
