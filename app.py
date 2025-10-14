# --- Imports originales de tu proyecto ---
from flask import Flask, render_template, url_for, request, jsonify
import os
import mysql.connector
from config import db_config

# ##### INICIO: Nuevos imports para manejo de usuarios y seguridad #####
from flask import redirect, flash, session
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from functools import wraps
from flask import abort
# ##### FIN: Nuevos imports #####


app = Flask(__name__)

# ##### INICIO: Configuración para sesiones y extensiones #####
app.config['SECRET_KEY'] = 'esta-es-una-clave-secreta-muy-segura-y-larga'
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'
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
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, nombre, email, rol FROM usuarios WHERE id = %s", (user_id,))
    user_data = cursor.fetchone()
    cursor.close()
    conn.close()
    if user_data:
        return User(id=user_data['id'], nombre=user_data['nombre'], email=user_data['email'], rol=user_data['rol'])
    return None
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


# ##### INICIO: CONTEXT PROCESSOR PARA EL CARRITO #####
@app.context_processor
def inject_cart_item_count():
    if current_user.is_authenticated:
        user_id = current_user.id
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        query = """
        SELECT SUM(ci.cantidad) as total_items
        FROM carrito_items ci
        JOIN carritos c ON ci.carrito_id = c.id
        WHERE c.usuario_id = %s
        """
        cursor.execute(query, (user_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        count = result['total_items'] if result and result['total_items'] is not None else 0
        return dict(cart_item_count=int(count))
    return dict(cart_item_count=0)
# ##### FIN: CONTEXT PROCESSOR #####


# --- RUTAS PÚBLICAS Y ORIGINALES DE TU APLICACIÓN ---

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/productos")
def productos():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos ORDER BY id DESC")
    lista_de_productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template("productos.html", productos=lista_de_productos)

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
    if current_user.is_authenticated:
        return redirect(url_for('index'))
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
            next_page = request.args.get('next')
            return redirect(next_page or url_for('productos'))
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


# ##### SECCIÓN DE GESTIÓN PARA EL ADMINISTRADOR #####
@app.route('/dashboard_admin')
@login_required
@admin_required
def dashboard_admin():
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM productos ORDER BY id DESC")
    lista_productos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('dashboard_admin.html', productos=lista_productos)

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
    return render_template('admin_form_producto.html', modo='add')

@app.route('/admin/edit_product/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
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
    cursor.execute("SELECT * FROM productos WHERE id = %s", (id,))
    producto = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('admin_form_producto.html', modo='edit', producto=producto)

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


# ##### RUTAS DEL CARRITO DE COMPRAS - VERSIÓN BASE DE DATOS #####
def get_user_cart_id(user_id):
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id FROM carritos WHERE usuario_id = %s", (user_id,))
    cart = cursor.fetchone()
    if cart:
        cart_id = cart['id']
    else:
        cursor.execute("INSERT INTO carritos (usuario_id) VALUES (%s)", (user_id,))
        conn.commit()
        cart_id = cursor.lastrowid
    cursor.close()
    conn.close()
    return cart_id

@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    user_id = current_user.id
    cart_id = get_user_cart_id(user_id)
    quantity = int(request.form.get('quantity', 1))
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM carrito_items WHERE carrito_id = %s AND producto_id = %s", (cart_id, product_id))
    item = cursor.fetchone()
    if item:
        new_quantity = item['cantidad'] + quantity
        cursor.execute("UPDATE carrito_items SET cantidad = %s WHERE id = %s", (new_quantity, item['id']))
    else:
        cursor.execute("INSERT INTO carrito_items (carrito_id, producto_id, cantidad) VALUES (%s, %s, %s)",
                       (cart_id, product_id, quantity))
    conn.commit()
    cursor.execute("SELECT nombre FROM productos WHERE id = %s", (product_id,))
    producto = cursor.fetchone()
    flash(f"¡'{producto['nombre']}' se ha añadido al carrito!", 'success')
    cursor.close()
    conn.close()
    return redirect(url_for('productos'))

@app.route('/cart')
@login_required
def cart():
    user_id = current_user.id
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    query = """
    SELECT 
        ci.producto_id,
        ci.cantidad,
        p.nombre,
        p.precio,
        p.imagen_url
    FROM carrito_items ci
    JOIN carritos c ON ci.carrito_id = c.id
    JOIN productos p ON ci.producto_id = p.id
    WHERE c.usuario_id = %s
    """
    cursor.execute(query, (user_id,))
    cart_items = cursor.fetchall()
    total_price = 0
    for item in cart_items:
        total_price += item['precio'] * item['cantidad']
    cursor.close()
    conn.close()
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

@app.route('/update_cart/<int:product_id>', methods=['POST'])
@login_required
def update_cart(product_id):
    user_id = current_user.id
    cart_id = get_user_cart_id(user_id)
    quantity = int(request.form.get('quantity', 1))
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    if quantity > 0:
        cursor.execute("UPDATE carrito_items SET cantidad = %s WHERE carrito_id = %s AND producto_id = %s",
                       (quantity, cart_id, product_id))
        flash('Cantidad actualizada.', 'success')
    else:
        cursor.execute("DELETE FROM carrito_items WHERE carrito_id = %s AND producto_id = %s", (cart_id, product_id))
        flash('Producto eliminado del carrito.', 'info')
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:product_id>', methods=['POST'])
@login_required
def remove_from_cart(product_id):
    user_id = current_user.id
    cart_id = get_user_cart_id(user_id)
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM carrito_items WHERE carrito_id = %s AND producto_id = %s", (cart_id, product_id))
    conn.commit()
    cursor.close()
    conn.close()
    flash('Producto eliminado del carrito.', 'info')
    return redirect(url_for('cart'))

# ##### INICIO: RUTAS DEL PROCESO DE CHECKOUT Y PEDIDOS #####

@app.route('/checkout')
@login_required
def checkout():
    # Esta ruta simplemente muestra la página de confirmación
    # En el futuro, aquí pedirías la dirección de envío
    user_id = current_user.id
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    # Volvemos a buscar los items del carrito para mostrarlos en el resumen
    query = """
    SELECT ci.cantidad, p.nombre, p.precio
    FROM carrito_items ci
    JOIN carritos c ON ci.carrito_id = c.id
    JOIN productos p ON ci.producto_id = p.id
    WHERE c.usuario_id = %s
    """
    cursor.execute(query, (user_id,))
    cart_items = cursor.fetchall()
    
    total_price = 0
    for item in cart_items:
        total_price += item['precio'] * item['cantidad']

    cursor.close()
    conn.close()
    return render_template('checkout.html', cart_items=cart_items, total_price=total_price)

@app.route('/place_order', methods=['POST'])
@login_required
def place_order():
    user_id = current_user.id
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # 1. Obtener los items del carrito del usuario
    cart_id = get_user_cart_id(user_id) # Usamos la función que ya teníamos
    query = "SELECT ci.producto_id, ci.cantidad, p.precio FROM carrito_items ci JOIN productos p ON ci.producto_id = p.id WHERE ci.carrito_id = %s"
    cursor.execute(query, (cart_id,))
    cart_items = cursor.fetchall()

    if not cart_items:
        flash('Tu carrito está vacío.', 'warning')
        return redirect(url_for('productos'))

    # 2. Calcular el total
    total_price = sum(item['precio'] * item['cantidad'] for item in cart_items)

    try:
        # 3. Crear el nuevo pedido en la tabla 'pedidos'
        cursor.execute("INSERT INTO pedidos (usuario_id, total) VALUES (%s, %s)", (user_id, total_price))
        pedido_id = cursor.lastrowid

        # 4. Mover cada item del carrito a la tabla 'pedido_items'
        for item in cart_items:
            cursor.execute("INSERT INTO pedido_items (pedido_id, producto_id, cantidad, precio_unitario) VALUES (%s, %s, %s, %s)",
                           (pedido_id, item['producto_id'], item['cantidad'], item['precio']))

        # 5. Vaciar el carrito de compras del usuario
        cursor.execute("DELETE FROM carrito_items WHERE carrito_id = %s", (cart_id,))
        
        # 6. Confirmar todos los cambios en la base de datos
        conn.commit()
        
        flash('¡Gracias por tu compra! Tu pedido ha sido realizado con éxito.', 'success')
        return redirect(url_for('mis_pedidos'))

    except mysql.connector.Error as err:
        conn.rollback() # Si algo falla, deshacemos todos los cambios
        flash('Hubo un error al procesar tu pedido. Por favor, inténtalo de nuevo.', 'danger')
        return redirect(url_for('checkout'))
    finally:
        cursor.close()
        conn.close()

@app.route('/mis_pedidos')
@login_required
def mis_pedidos():
    user_id = current_user.id
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    # Buscamos todos los pedidos del usuario, del más reciente al más antiguo
    cursor.execute("SELECT * FROM pedidos WHERE usuario_id = %s ORDER BY fecha_pedido DESC", (user_id,))
    lista_de_pedidos = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('mis_pedidos.html', pedidos=lista_de_pedidos)

# ##### FIN: RUTAS DEL PROCESO DE CHECKOUT Y PEDIDOS #####

if __name__ == '__main__':
    app.run(debug=True)