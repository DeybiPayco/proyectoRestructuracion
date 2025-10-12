from flask import Flask, render_template, url_for, request, redirect, flash
import os

# Inicializar la aplicacion en flask
app = Flask(__name__)

# Necesario para usar flash messages (mensajes temporales)
# ¡IMPORTANTE!: CAMBIA 'tu_clave_secreta_aqui' por una cadena aleatoria y compleja en producción
app.secret_key = 'una_clave_secreta_super_segura_y_unica' 


# Rutas

@app.route("/")
def index():
    # Lógica para cargar imágenes
    ruta = os.path.join(app.root_path, 'static', 'img')
    
    imagenes = []
    if os.path.exists(ruta):
        imagenes = [url_for('static', filename=f'img/{img}') 
                    for img in os.listdir(ruta) 
                    if img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        
    # Renderizamos la plantilla con las imágenes y los mensajes flash disponibles
    return render_template("index.html", imagenes=imagenes)

@app.route('/enviar_formulario', methods=['POST'])
def manejar_formulario():
    if request.method == 'POST':
        
        # 1. Capturar los datos del formulario
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        preferencia = request.form.get('preferencia')
        ocasion = request.form.get('ocasion')
        
        # 2. Lógica de Negocio (Guardar datos)
        print("--- NUEVO CLIENTE REGISTRADO ---")
        print(f"Nombre: {nombre}, Email: {email}")
        print(f"Preferencia: {preferencia}, Ocasion: {ocasion}")
        # Aquí se simula el guardado.
        
        # 3. Mostrar el mensaje de agradecimiento
        # flash('El mensaje', 'categoría') - 'success' es una categoría común, aunque no se usa aquí.
        flash(f'¡Gracias, {nombre}! Tus preferencias han sido guardadas. Revisa tu correo, ¡te espera un descuento!', 'success')
        
        # 4. Redirigir a la página principal (PRG pattern)
        # Esto hace que el usuario vea la página principal con el mensaje de éxito.
        return redirect(url_for('index'))
    
    return redirect(url_for('index'))


# Ejecutar mi servidor
if __name__ == '__main__':
    # Usar el puerto 5000 por defecto
    app.run(debug=True)