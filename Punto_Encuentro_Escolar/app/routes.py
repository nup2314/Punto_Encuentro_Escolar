import sqlite3
from datetime import date
from pathlib import Path

from flask import Blueprint, flash, redirect, render_template, request, url_for

bp = Blueprint("main", __name__)

# objetos.db está en la carpeta raíz del proyecto (dos niveles arriba de este archivo)
DB_PATH = Path(__file__).resolve().parent.parent / "objetos.db"


def obtener_conexion():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # permite usar los resultados como diccionarios
    return conn


def crear_tabla():
    conn = obtener_conexion()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS objetos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            categoria TEXT NOT NULL,
            lugar TEXT NOT NULL,
            fecha TEXT NOT NULL,
            descripcion TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


@bp.route("/")
def inicio():
    """Lista de objetos con búsqueda y filtro por categoría."""
    busqueda = request.args.get("q", "").strip()
    categoria = request.args.get("categoria", "").strip()

    consulta = "SELECT * FROM objetos WHERE 1=1"
    datos = []
    if busqueda:
        consulta += " AND (nombre LIKE ? OR descripcion LIKE ? OR lugar LIKE ?)"
        datos += [f"%{busqueda}%"] * 3
    if categoria:
        consulta += " AND categoria = ?"
        datos.append(categoria)
    consulta += " ORDER BY fecha DESC, id DESC"

    conn = obtener_conexion()
    objetos = conn.execute(consulta, datos).fetchall()
    categorias = [
        fila["categoria"]
        for fila in conn.execute("SELECT DISTINCT categoria FROM objetos ORDER BY categoria")
    ]
    conn.close()

    return render_template(
        "index.html",
        objetos=objetos,
        categorias=categorias,
        busqueda=busqueda,
        categoria=categoria,
    )


@bp.route("/nuevo", methods=["GET", "POST"])
def nuevo():
    """Formulario para registrar un objeto encontrado."""
    campos = ["nombre", "categoria", "lugar", "fecha", "descripcion"]
    valores = {c: request.form.get(c, "").strip() for c in campos}

    if request.method == "POST":
        if all(valores.values()):
            conn = obtener_conexion()
            conn.execute(
                "INSERT INTO objetos (nombre, categoria, lugar, fecha, descripcion) "
                "VALUES (?, ?, ?, ?, ?)",
                [valores[c] for c in campos],
            )
            conn.commit()
            conn.close()
            flash("Objeto registrado correctamente.", "ok")
            return redirect(url_for("main.inicio"))
        flash("Completa todos los campos.", "error")
    else:
        valores["fecha"] = date.today().isoformat()

    return render_template("nuevo.html", valores=valores)
