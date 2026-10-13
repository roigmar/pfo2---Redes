"""Servidor web y API REST del sistema de gestión de tareas."""

import os
import sqlite3
from functools import wraps
from typing import Callable

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from database import buscar_usuario, crear_usuario, inicializar_base_datos, obtener_tareas


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get(
    "SECRET_KEY", "clave-de-desarrollo-cambiar-en-produccion"
)
inicializar_base_datos()


def respuesta_error(mensaje: str, estado: int):
    """Devuelve un error JSON con un formato uniforme."""
    return jsonify({"exito": False, "mensaje": mensaje}), estado


def usuario_con_sesion(funcion: Callable):
    """Protege una ruta que necesita un usuario autenticado."""
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        if "usuario" not in session:
            return respuesta_error("Debes iniciar sesión para continuar.", 401)
        return funcion(*args, **kwargs)

    return envoltura


@app.get("/")
def inicio():
    """Redirige al formulario de inicio de sesión."""
    return redirect(url_for("pagina_login"))


@app.get("/registro")
def pagina_registro():
    """Muestra el formulario de registro."""
    return render_template("registro.html")


@app.post("/registro")
def registrar():
    """Valida y registra un usuario con contraseña hasheada."""
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return respuesta_error("El cuerpo debe ser un objeto JSON válido.", 400)

    usuario = str(datos.get("usuario", "")).strip()
    contraseña = str(datos.get("contraseña", ""))
    if not usuario or not contraseña.strip():
        return respuesta_error("El usuario y la contraseña son obligatorios.", 400)

    if buscar_usuario(usuario) is not None:
        return respuesta_error("El usuario ya existe. Elegí otro nombre.", 409)

    try:
        crear_usuario(usuario, generate_password_hash(contraseña))
    except sqlite3.IntegrityError:
        return respuesta_error("El usuario ya existe. Elegí otro nombre.", 409)

    return jsonify({"exito": True, "mensaje": "Usuario registrado correctamente."}), 201


@app.get("/login")
def pagina_login():
    """Muestra el formulario de inicio de sesión."""
    return render_template("login.html")


@app.post("/login")
def iniciar_sesion():
    """Comprueba las credenciales y crea la sesión del usuario."""
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return respuesta_error("El cuerpo debe ser un objeto JSON válido.", 400)

    usuario = str(datos.get("usuario", "")).strip()
    contraseña = str(datos.get("contraseña", ""))
    registro = buscar_usuario(usuario) if usuario else None
    if registro is None or not check_password_hash(registro["contraseña_hash"], contraseña):
        return respuesta_error("El usuario o la contraseña no son correctos.", 401)

    session.clear()
    session["usuario"] = registro["usuario"]
    return jsonify({"exito": True, "mensaje": "Inicio de sesión correcto."})


@app.get("/tareas")
@usuario_con_sesion
def tareas():
    """Muestra la página de bienvenida del usuario autenticado."""
    registro = buscar_usuario(session["usuario"])
    lista_tareas = obtener_tareas(registro["id"]) if registro else []
    return render_template(
        "bienvenida.html",
        usuario=session["usuario"],
        tareas=lista_tareas,
    )


@app.post("/logout")
def cerrar_sesion():
    """Elimina la sesión activa."""
    session.clear()
    return jsonify({"exito": True, "mensaje": "Sesión cerrada correctamente."})


if __name__ == "__main__":
    app.run(debug=True)
