# 1. Importaciones necesarias
# Añadimos jsonify para la respuesta AJAX y mysql.connector para la base de datos.
from flask import Flask, render_template, url_for, request, jsonify
import os
import mysql.connector
from config import db_config  # Importamos la configuración de la base de datos

# Inicializar la aplicacion en flask
app = Flask(__name__)

# La clave secreta ya no es necesaria si no usamos flash, la he comentado.
# app.secret_key = 'una_clave_secreta_super_segura_y_unica' 

# Ruta principal que muestra la página
@app.route("/")
def index():
    # Tu lógica mejorada para cargar imágenes (¡está muy bien!)
    ruta_imagenes = os.path.join(app.static_folder, 'img')
    imagenes = []
    if os.path.exists(ruta_imagenes):
        imagenes = [url_for('static', filename=f'img/{img}') 
                    for img in os.listdir(ruta_imagenes) 
                    if img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            
    return render_template("index.html", imagenes=imagenes)

# Ruta para procesar el formulario enviado por JavaScript
@app.route('/enviar_formulario', methods=['POST'])
def manejar_formulario():
    if request.method == 'POST':
        # 1. Capturar los datos del formulario
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        preferencia = request.form.get('preferencia')
        ocasion = request.form.get('ocasion')
        
        # 2. Conectar y guardar en la base de datos
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            
            query = "INSERT INTO clientes (nombre, email, preferencia, ocasion) VALUES (%s, %s, %s, %s)"
            values = (nombre, email, preferencia, ocasion)
            
            cursor.execute(query, values)
            conn.commit()
            
            # 3. Preparar el mensaje de éxito personalizado
            primer_nombre = nombre.split()[0] if nombre else "Amigo(a)"
            mensaje_exito = f"¡Gracias, {primer_nombre}! Tus preferencias han sido guardadas. Revisa tu correo, ¡te espera un descuento!"
            
            # 4. Enviar respuesta JSON al front-end (en lugar de flash y redirect)
            return jsonify({'status': 'success', 'message': mensaje_exito})

        except mysql.connector.Error as err:
            print(f"Error al conectar con la base de datos: {err}")
            return jsonify({'status': 'error', 'message': 'No pudimos guardar tus datos. Inténtalo más tarde.'}), 500
            
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()
    
    # Si la petición no es POST, simplemente no hacemos nada visible para el usuario.
    return jsonify({'status': 'error', 'message': 'Método no permitido.'}), 405


# Ejecutar mi servidor
if __name__ == '__main__':
    app.run(debug=True)

