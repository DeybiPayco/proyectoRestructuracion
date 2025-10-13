# --- Imports originales de tu proyecto ---
from flask import Flask, render_template, url_for, request, jsonify
import os
import mysql.connector
from config import db_config

# ##### INICIO: Nuevos imports para manejo de usuarios y seguridad #####
from flask import redirect, flash, session # Para redirigir, mostrar mensajes y manejar sesiones
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from functools import wraps # Necesario para crear nuestro decorador de admin
from flask import abort # Para restringir acceso si no se cumplen los roles
# ##### FIN: Nuevos imports #####


app = Flask(__name__)

# ##### INICIO: Configuración para sesiones y extensiones #####
app.config['SECRET_KEY'] = 'esta-es-una-clave-secreta-muy-segura-y-larga'
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, inicia sesión para ver esta página.'
login_manager.login_message_category = 'info'
# ##### FIN: Configuración #####


# ##### INICIO: Modelo de Usuario y cargador para Flask-Login #####
class User(UserMixin):
    def __init__(self, id, nombre, email, rol):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.rol = rol

@login_manager.user_loader
def load_user(user_id):
    conn = None
    cursor = None
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nombre, email, rol FROM usuarios WHERE id = %s", (user_id,))
        user_data = cursor.fetchone()
        if user_data:
            return User(id=user_data['id'], nombre=user_data['nombre'], email=user_data['email'], rol=user_data['rol'])
        return None
    except mysql.connector.Error as err:
        print(f"Error al cargar usuario: {err}")
        return None
    finally:
        if cursor:
            cursor.close()
        if conn and conn.is_connected():
            conn.close()
# ##### FIN: Modelo de Usuario y cargador #####


# ##### INICIO: Decorador para rutas de Administrador #####
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.rol != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function
# ##### FIN: Decorador de Admin #####


# --- RUTAS PÚBLICAS Y ORIGINALES DE TU APLICACIÓN ---

@app.route("/")
def index():
    ruta_imagenes = os.path.join(app.static_folder, 'img')
    imagenes = []
    if os.path.exists(ruta_imagenes):
        imagenes = [url_for('static', filename=f'img/{img}') 
                    for img in os.listdir(ruta_imagenes) 
                    if img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
            
    return render_template("index.html", imagenes=imagenes)

# VERSIÓN NUEVA Y DINÁMICA
@app.route("/productos")
def productos():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos ORDER BY id DESC") # Buscamos todos los productos
    lista_de_productos = cursor.fetchall()
    cursor.close()
    conn.close()
    # Le pasamos la lista de productos a la plantilla HTML
    return render_template("productos.html", productos=lista_de_productos)

@app.route('/enviar_formulario', methods=['POST'])
def manejar_formulario():
    # ... (Tu código original para el formulario de contacto se mantiene igual)
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


# --- RUTAS DE AUTENTICACIÓN (LOGIN, REGISTRO, LOGOUT) ---

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    # ... (Tu código de registro se mantiene igual)
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        email = request.form.get('email')
        password = request.form.get('password')
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO usuarios (nombre, email, password_hash, rol) VALUES (%s, %s, %s, 'cliente')", 
                           (nombre, email, password_hash))
            conn.commit()
            flash('¡Registro exitoso! Ya puedes iniciar sesión.', 'success')
            return redirect(url_for('login'))
        except mysql.connector.Error as err:
            if err.errno == 1062:
                flash('El correo electrónico ya está registrado.', 'danger')
            else:
                flash(f'Ocurrió un error en la base de datos: {err}', 'danger')
            return redirect(url_for('registro'))
        finally:
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and conn.is_connected():
                conn.close()
    return render_template('registro.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # ... (Tu código de login se mantiene igual)
    if request.method == 'POST':
        email = request.form.get('email')
        password_ingresada = request.form.get('password')
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
        user_data = cursor.fetchone()
        cursor.close()
        conn.close()
        if user_data and bcrypt.check_password_hash(user_data['password_hash'], password_ingresada):
            usuario_obj = User(id=user_data['id'], nombre=user_data['nombre'], email=user_data['email'], rol=user_data['rol'])
            login_user(usuario_obj)
            flash('Inicio de sesión correcto.', 'success')
            if usuario_obj.rol == 'admin':
                return redirect(url_for('dashboard_admin'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Email o contraseña incorrectos. Inténtalo de nuevo.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado la sesión exitosamente.', 'info')
    return redirect(url_for('index'))


# ##### INICIO: SECCIÓN COMPLETA DE GESTIÓN PARA EL ADMINISTRADOR #####

# RUTA PRINCIPAL DEL PANEL DE ADMIN: AHORA MUESTRA LA LISTA DE PRODUCTOS
# (Esta versión reemplaza a la anterior para evitar el error de duplicado)
@app.route('/dashboard_admin')
@login_required
@admin_required
def dashboard_admin():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos ORDER BY id DESC") # Ordenamos para ver los más nuevos primero
    lista_productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('dashboard_admin.html', productos=lista_productos)

# RUTA PARA MOSTRAR EL FORMULARIO Y PROCESAR LA CREACIÓN DE UN NUEVO PRODUCTO
@app.route('/admin/add_product', methods=['GET', 'POST'])
@login_required
@admin_required
def add_product():
    if request.method == 'POST':
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        imagen_url = request.form['imagen_url']

        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("INSERT INTO productos (nombre, descripcion, precio, imagen_url) VALUES (%s, %s, %s, %s)",
                       (nombre, descripcion, precio, imagen_url))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('¡Producto añadido exitosamente!', 'success')
        return redirect(url_for('dashboard_admin'))

    # Si el método es GET, solo muestra el formulario
    return render_template('admin_form_producto.html', modo='add')

# RUTA PARA MOSTRAR EL FORMULARIO (CON DATOS) Y PROCESAR LA EDICIÓN DE UN PRODUCTO
@app.route('/admin/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        # Si el formulario se envía, actualiza los datos
        nombre = request.form['nombre']
        descripcion = request.form['descripcion']
        precio = request.form['precio']
        imagen_url = request.form['imagen_url']

        cursor.execute("UPDATE productos SET nombre=%s, descripcion=%s, precio=%s, imagen_url=%s WHERE id=%s",
                       (nombre, descripcion, precio, imagen_url, id))
        conn.commit()
        cursor.close()
        conn.close()
        
        flash('¡Producto actualizado exitosamente!', 'success')
        return redirect(url_for('dashboard_admin'))

    # Si el método es GET, busca el producto y muestra el formulario con sus datos
    cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
    producto = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('admin_form_producto.html', modo='edit', producto=producto)

# RUTA PARA PROCESAR LA ELIMINACIÓN DE UN PRODUCTO
@app.route('/admin/delete_product/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_product(id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM productos WHERE id = %s", (id,))
    conn.commit()
    cursor.close()
    conn.close()
    
    flash('Producto eliminado exitosamente.', 'danger')
    return redirect(url_for('dashboard_admin'))

# ##### FIN: SECCIÓN COMPLETA DE GESTIÓN PARA EL ADMINISTRADOR #####


if __name__ == '__main__':
    app.run(debug=True)