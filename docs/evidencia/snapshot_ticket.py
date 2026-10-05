"""Genera tickets de 3 ventas de ejemplo para comparar antes/despues de un refactor.

Uso (desde la raiz del repo):
    python docs/evidencia/snapshot_ticket.py <archivo_salida>
"""

import os
import sys

RAIZ = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
sys.path.insert(0, os.path.join(RAIZ, "src"))

import gestor  # noqa: E402

gestor.reiniciar_sistema()
gestor.agregarProducto("A1", "Cafe de grano", 10.0, 500)
gestor.agregarProducto("B2", "Azucar", 100.0, 500)

casos = [
    ("1) sin descuento", "A1", 2, ""),
    ("2) con descuento por volumen (10%)", "B2", 20, ""),
    ("3) cliente VIP con descuento por volumen (5% + 2%)", "B2", 6, "VIP007"),
]

lineas = []
for titulo, codigo, cantidad, cliente in casos:
    venta = gestor.registrar_venta(codigo, cantidad, cliente)
    lineas.append("=== " + titulo + " ===")
    lineas.append(repr(venta["ticket"]))
    lineas.append(venta["ticket"].rstrip("\n"))
    datos = {k: v for k, v in venta.items() if k not in ("fecha", "ticket")}
    lineas.append("dict (sin fecha ni ticket): " + repr(datos))
    lineas.append("")

with open(sys.argv[1], "w", encoding="utf-8", newline="\n") as f:
    f.write("\n".join(lineas) + "\n")
