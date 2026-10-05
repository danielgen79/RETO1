"""Ejecuta src/main.py con entradas fijas y guarda toda la salida.

main.py no tiene tests, asi que este script sirve para comprobar que un
refactor no cambia lo que el menu imprime ni los datos que guarda.

Corre tres escenarios, siempre en una carpeta temporal (el datos_ejemplo.json
original no se modifica):
  A) con una copia de datos_ejemplo.json: recorre todas las opciones, incluidas
     una opcion invalida, ventas (con VIP), cotizaciones y errores.
  B) sin archivo de datos: listas vacias y la rama "No hay productos...".
  C) con un archivo de datos corrupto.

Uso (desde la raiz del repo):
    python docs/evidencia/snapshot_menu.py <archivo_salida>

La fecha de las ventas se omite al mostrar los datos guardados, porque cambia
en cada ejecucion.
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
MAIN = os.path.join(RAIZ, "src", "main.py")
DATOS_ORIGINAL = os.path.join(RAIZ, "datos_ejemplo.json")
ARCHIVO = "datos_ejemplo.json"

ENTRADAS_A = [
    "9",  # opcion invalida
    "",  # opcion vacia
    "4",  # reporte de inventario
    "7",  # alertas de stock bajo (A003 y B002)
    # 1) agregar producto
    "1", "Z9", "Producto nuevo", "abc", "25.5", "3.9",  # precio no numerico
    "1", "Z9", "Otro", "10", "5",  # codigo duplicado
    "1", "Z8", "Barato", "0", "5",  # precio invalido
    "1", "Z7", "Sin stock", "10", "-1",  # stock invalido
    "1", "", "Sin codigo", "10", "5",  # codigo vacio
    # 2) registrar venta
    "2", "A002", "3", "",  # sin descuento
    "2", "A001", "5", "VIP007",  # descuento por volumen + extra VIP
    "2", "B001", "18", "",  # descuento por volumen, deja stock en 0
    "2", "A001", "abc", "2", "",  # cantidad no numerica
    "2", "NOPE", "1", "",  # producto inexistente
    "2", "A003", "10", "",  # stock insuficiente
    "2", "A003", "0", "",  # cantidad invalida
    "2", "", "1", "",  # codigo vacio
    "2", "A002", "1", "VIP",  # prefijo VIP pero compra chica
    "2", "C001", "4", "",  # empata en unidades con A002
    # 3) cotizar
    "3", "A001", "2",
    "3", "A001", "40",  # descuento alto
    "3", "NOPE", "1",  # producto inexistente
    "3", "A001", "0",  # cantidad invalida
    "3", "", "1",  # codigo vacio
    # 4-7) reportes
    "4", "5", "6", "7",
    "8",  # guardar y salir
]

ENTRADAS_B = [
    "7", "6", "5", "4",  # todo vacio
    "1", "A1", "Cafe", "10", "5",
    "7", "6", "4", "5",
    "8",
]

ENTRADAS_C = ["4", "8"]


def ejecutar(titulo, entradas, contenido_datos):
    """Corre main.py en una carpeta temporal y regresa el texto del escenario."""
    with tempfile.TemporaryDirectory() as tmp:
        ruta_datos = os.path.join(tmp, ARCHIVO)
        if contenido_datos == "copia":
            shutil.copyfile(DATOS_ORIGINAL, ruta_datos)
        elif contenido_datos is not None:
            with open(ruta_datos, "w", encoding="utf-8") as f:
                f.write(contenido_datos)

        entorno = dict(os.environ, PYTHONIOENCODING="utf-8")
        entorno["PYTHONDONTWRITEBYTECODE"] = "1"
        proceso = subprocess.run(
            [sys.executable, MAIN],
            input="\n".join(entradas) + "\n",
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=tmp,
            env=entorno,
            check=False,
        )
        salida = (proceso.stdout + proceso.stderr).replace(tmp, "<TMP>")
        salida = salida.replace(RAIZ, "<RAIZ>")

        guardado = "(no se genero archivo)"
        if os.path.exists(ruta_datos):
            with open(ruta_datos, encoding="utf-8") as f:
                try:
                    datos = json.load(f)
                    for venta in datos.get("ventas", []):
                        venta.pop("fecha", None)
                    guardado = json.dumps(datos, indent=2, ensure_ascii=False)
                except ValueError:
                    guardado = "(archivo no es JSON valido)"

    partes = [
        "#" * 70,
        "# ESCENARIO " + titulo,
        "#" * 70,
        "--- entradas (una por linea) ---",
        repr(entradas),
        "--- codigo de salida: " + str(proceso.returncode) + " ---",
        "--- salida ---",
        salida,
        "--- datos guardados (sin fecha) ---",
        guardado,
        "",
    ]
    return "\n".join(partes)


def main():
    resultado = [
        ejecutar("A: con copia de datos_ejemplo.json", ENTRADAS_A, "copia"),
        ejecutar("B: sin archivo de datos", ENTRADAS_B, None),
        ejecutar("C: archivo de datos corrupto", ENTRADAS_C, "esto no es json"),
    ]
    with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(resultado))


if __name__ == "__main__":
    main()
