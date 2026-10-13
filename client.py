"""Cliente interactivo de consola para la API de tareas."""

import getpass
from typing import Optional

import requests


URL_BASE = "http://127.0.0.1:5000"


def mostrar_respuesta(respuesta: requests.Response) -> None:
    """Imprime el mensaje JSON de una respuesta de la API."""
    try:
        datos = respuesta.json()
        print(f"{datos.get('mensaje', 'Respuesta recibida.')} (HTTP {respuesta.status_code})")
    except ValueError:
        print(f"Respuesta no esperada del servidor (HTTP {respuesta.status_code}).")


def pedir_datos_usuario() -> Optional[tuple[str, str]]:
    """Solicita usuario y contraseña, validando que no estén vacíos."""
    usuario = input("Usuario: ").strip()
    contraseña = getpass.getpass("Contraseña: ")
    if not usuario or not contraseña:
        print("El usuario y la contraseña no pueden estar vacíos.")
        return None
    return usuario, contraseña


def registrar(cliente: requests.Session) -> None:
    """Envía los datos del registro."""
    datos = pedir_datos_usuario()
    if datos is None:
        return
    try:
        respuesta = cliente.post(
            f"{URL_BASE}/registro",
            json={"usuario": datos[0], "contraseña": datos[1]},
            timeout=10,
        )
        mostrar_respuesta(respuesta)
    except requests.RequestException as error:
        print(f"No se pudo conectar con el servidor: {error}")


def iniciar_sesion(cliente: requests.Session) -> None:
    """Envía las credenciales y conserva la cookie de sesión."""
    datos = pedir_datos_usuario()
    if datos is None:
        return
    try:
        respuesta = cliente.post(
            f"{URL_BASE}/login",
            json={"usuario": datos[0], "contraseña": datos[1]},
            timeout=10,
        )
        mostrar_respuesta(respuesta)
    except requests.RequestException as error:
        print(f"No se pudo conectar con el servidor: {error}")


def ver_tareas(cliente: requests.Session) -> None:
    """Solicita la página protegida e imprime un resumen."""
    try:
        respuesta = cliente.get(f"{URL_BASE}/tareas", timeout=10)
        print(f"Estado HTTP: {respuesta.status_code}")
        if respuesta.ok:
            texto = " ".join(respuesta.text.split())
            print(f"Resumen: {texto[:300]}...")
        else:
            try:
                print(f"Error: {respuesta.json().get('mensaje', 'Acceso rechazado.')}")
            except ValueError:
                print("El servidor rechazó la solicitud.")
    except requests.RequestException as error:
        print(f"No se pudo conectar con el servidor: {error}")


def ejecutar() -> None:
    """Ejecuta el menú principal hasta que la persona elija salir."""
    cliente = requests.Session()
    opciones = {
        "1": ("Registrarse", registrar),
        "2": ("Iniciar sesión", iniciar_sesion),
        "3": ("Ver tareas", ver_tareas),
    }
    while True:
        print("\n=== Sistema de gestión de tareas ===")
        for numero, (nombre, _) in opciones.items():
            print(f"{numero}) {nombre}")
        print("4) Salir")
        opcion = input("Elegí una opción: ").strip()
        if opcion == "4":
            print("¡Hasta pronto!")
            break
        if opcion in opciones:
            opciones[opcion][1](cliente)
        else:
            print("Opción no válida. Elegí un número del 1 al 4.")


if __name__ == "__main__":
    ejecutar()
