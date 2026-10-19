from flask import Flask


def create_app():
    # templates y static están en la carpeta raíz del proyecto, junto a run.py
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.config["SECRET_KEY"] = "cambia-esta-clave"  # necesaria para los mensajes flash

    from .routes import bp, crear_tabla
    app.register_blueprint(bp)

    crear_tabla()  # crea la tabla si todavía no existe
    return app
