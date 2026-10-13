"""Funciones de acceso a la base de datos SQLite del proyecto."""

from pathlib import Path
import sqlite3
from typing import Optional


RUTA_BASE = Path(__file__).with_name("database.db")


def obtener_conexion() -> sqlite3.Connection:
    """Abre una conexión SQLite con filas accesibles por nombre."""
    conexion = sqlite3.connect(RUTA_BASE)
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar_base_datos() -> None:
    """Crea las tablas necesarias si todavía no existen."""
    with obtener_conexion() as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario TEXT UNIQUE NOT NULL,
                contraseña_hash TEXT NOT NULL
            )
            """
        )
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS tareas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                titulo TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                completada INTEGER NOT NULL DEFAULT 0,
                FOREIGN KEY (usuario_id) REFERENCES usuarios (id)
            )
            """
        )


def buscar_usuario(usuario: str) -> Optional[sqlite3.Row]:
    """Busca un usuario por su nombre, sin concatenar SQL."""
    with obtener_conexion() as conexion:
        return conexion.execute(
            "SELECT id, usuario, contraseña_hash FROM usuarios WHERE usuario = ?",
            (usuario,),
        ).fetchone()


def crear_usuario(usuario: str, contraseña_hash: str) -> None:
    """Guarda un usuario nuevo y su contraseña protegida."""
    with obtener_conexion() as conexion:
        conexion.execute(
            "INSERT INTO usuarios (usuario, contraseña_hash) VALUES (?, ?)",
            (usuario, contraseña_hash),
        )


def obtener_tareas(usuario_id: int) -> list[sqlite3.Row]:
    """Devuelve las tareas de un usuario, ordenadas por identificador."""
    with obtener_conexion() as conexion:
        return conexion.execute(
            """
            SELECT id, titulo, descripcion, completada
            FROM tareas
            WHERE usuario_id = ?
            ORDER BY id
            """,
            (usuario_id,),
        ).fetchall()


def crear_tarea(
    usuario_id: int, titulo: str, descripcion: str, completada: bool = False
) -> None:
    """Guarda una tarea asociada a un usuario."""
    with obtener_conexion() as conexion:
        conexion.execute(
            """
            INSERT INTO tareas (usuario_id, titulo, descripcion, completada)
            VALUES (?, ?, ?, ?)
            """,
            (usuario_id, titulo, descripcion, int(completada)),
        )
