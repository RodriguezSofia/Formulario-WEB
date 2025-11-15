from flask import Flask, request, jsonify, render_template, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor
import traceback
import os
import datetime 


# Configuración de la aplicación
app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'database': 'Formulario',
    'user': 'postgres',
    'password': '123456',
    'port': 5432
}

# Función para conectar la base de datos
def conectar_bd():
    try:
        conexion = psycopg2.connect(**DB_CONFIG)
        return conexion
    except psycopg2.Error as e:
        print(f" Error al conectar a la base de datos: {e}")
        return None

# Crear tabla si no existe
def crear_tabla():
    conexion = conectar_bd()
    if conexion:
        cursor = conexion.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS Registros (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            apellido VARCHAR(100) NOT NULL,
            direccion VARCHAR(100),
            telefono VARCHAR(20),
            correo_electronico VARCHAR(100) NOT NULL,
            mensaje TEXT,
            creado TIMESTAMP DEFAULT NOW()
        );
        """)
        conexion.commit()
        cursor.close()
        conexion.close()

# Página principal
@app.route('/')
def inicio():
    return render_template('index.html')

# Ruta para guardar contacto
# Ruta para guardar contacto (versión que recarga la página)
@app.route('/guardar', methods=['POST'])
def guardar_contactos():
    try:
        conexion = conectar_bd()
        if conexion is None:
            return "Error: No se pudo conectar a la base de datos", 500

        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        direccion = request.form.get('direccion', '').strip()
        telefono = request.form.get('telefono', '').strip()
        correo_electronico = request.form.get('correo_electronico', '').strip()
        mensaje = request.form.get('mensaje', '').strip()

        if not nombre or not apellido or not correo_electronico:
            return "Error: Faltan datos obligatorios", 400

        cursor = conexion.cursor()
        sql_insertar = """
        INSERT INTO Registros (nombre, apellido, direccion, telefono, correo_electronico, mensaje)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(sql_insertar, (nombre, apellido, direccion, telefono, correo_electronico, mensaje))
        conexion.commit()
        cursor.close()
        conexion.close()

        #Redirige a la página principal después de guardar
        return redirect(url_for('inicio'))

    except Exception as e:
        print(f" Error al guardar el contacto: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Error al procesar la solicitud'}), 500

# Ruta para ver todos los contactos
@app.route('/ver', methods=['GET'])
def ver_registros():
    try:
        conexion = conectar_bd()
        if conexion is None:
            return jsonify({'error': 'No se pudo conectar a la base de datos'}), 500
        
        cursor = conexion.cursor(cursor_factory=RealDictCursor)
        cursor.execute("SELECT * FROM Registros ORDER BY creado DESC;")
        contactos = cursor.fetchall()
        cursor.close()
        conexion.close()

        for contacto in contactos:
            if contacto['creado']:
                contacto['creado'] = contacto['creado'].strftime('%Y-%m-%d %H:%M:%S')

        return jsonify(contactos), 200

    except Exception as e:
        print(f" Error al obtener contactos: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Error al obtener contactos'}), 500

# Inicio del servidor
if __name__ == '__main__':
    print(" Iniciando servidor...")
    crear_tabla()
    app.run(debug=True, host='0.0.0.0', port=5000)