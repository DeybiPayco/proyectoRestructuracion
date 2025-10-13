from flask import Flask, render_template, url_for, request, jsonify
import os
import mysql.connector
from config import db_config

app = Flask(__name__)

@app.route("/")
def index():
    ruta_imagenes = os.path.join(app.static_folder, 'img')
    imagenes = []
    if os.path.exists(ruta_imagenes):
        imagenes = [url_for('static', filename=f'img/{img}') 
                    for img in os.listdir(ruta_imagenes) 
                    if img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            
    return render_template("index.html", imagenes=imagenes)

@app.route("/productos")
def productos():
    return render_template("productos.html")

@app.route('/enviar_formulario', methods=['POST'])
def manejar_formulario():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        preferencia = request.form.get('preferencia')
        ocasion = request.form.get('ocasion')
        
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            query = "INSERT INTO clientes (nombre, email, preferencia, ocasion) VALUES (%s, %s, %s, %s)"
            values = (nombre, email, preferencia, ocasion)
            
            cursor.execute(query, values)
            conn.commit()
            
            primer_nombre = nombre.split()[0] if nombre else "Amigo(a)"
            mensaje_exito = f"¡Gracias, {primer_nombre}! Tus preferencias han sido guardadas. Revisa tu correo, ¡te espera un descuento!"
            
            return jsonify({'status': 'success', 'message': mensaje_exito})

        except mysql.connector.Error as err:
            print(f"Error al conectar con la base de datos: {err}")
            return jsonify({'status': 'error', 'message': 'No pudimos guardar tus datos. Inténtalo más tarde.'}), 500
            
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()
    
    return jsonify({'status': 'error', 'message': 'Método no permitido.'}), 405

if __name__ == '__main__':
    app.run(debug=True)