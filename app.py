from  flask  import  Flask, render_template,url_for
import os
#inicializar la aplicacion en flask
app = Flask(__name__)
#rutas
@app.route("/")
def index():
    ruta = os.path.join(app.static_folder, 'img')
    imagenes = [url_for('static', filename=f'img/{img}') for img in os.listdir(ruta) if img.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]
    return render_template("index.html", imagenes=imagenes)

#ejecutar mi servidor
if __name__ == '__main__':
    app.run(debug=True)