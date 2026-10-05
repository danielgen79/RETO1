"""Pruebas de caracterizacion: fijan el comportamiento ACTUAL en casos limite.

No dicen que el comportamiento sea el ideal, solo que no cambie al refactorizar.
Con precio unitario de $1.00 el subtotal es igual a la cantidad, lo que permite
ubicar los umbrales con exactitud.
"""

import gestor
import pytest


def _alta_producto(codigo="A1", precio=1.0, stock=5000):
    assert gestor.agregarProducto(codigo, "Producto de prueba", precio, stock)


# ---------------------------------------------------------------------------
# Limites de descuento por volumen (500 y 1000)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("cantidad", "descuento", "total"),
    [
        (499, 0, 578.84),  # justo debajo de 500: sin descuento
        (500, 25.0, 551.0),  # justo en 500: 5%
        (999, 49.95, 1100.9),  # justo debajo de 1000: sigue en 5%
        (1000, 100.0, 1044.0),  # justo en 1000: 10%
    ],
)
def test_limites_de_descuento_por_volumen(cantidad, descuento, total):
    _alta_producto()
    venta = gestor.registrar_venta("A1", cantidad)
    assert venta["subtotal"] == cantidad
    assert venta["descuento"] == descuento
    assert venta["total"] == total


@pytest.mark.parametrize("cantidad", [499, 500, 999, 1000])
def test_cotizar_coincide_con_la_venta_en_los_limites(cantidad):
    _alta_producto()
    estimado = gestor.cotizar("A1", cantidad)
    venta = gestor.registrar_venta("A1", cantidad)
    assert estimado == venta["total"]


# ---------------------------------------------------------------------------
# Limite VIP (la compra, ya con descuento, debe pasar de $200)
# ---------------------------------------------------------------------------


def test_vip_con_compra_justo_en_200_no_recibe_extra():
    _alta_producto()
    venta = gestor.registrar_venta("A1", 200, "VIP001")
    assert venta["descuento"] == 0
    assert venta["total"] == 232.0


def test_vip_con_compra_justo_arriba_de_200_recibe_extra():
    _alta_producto()
    venta = gestor.registrar_venta("A1", 201, "VIP001")
    # 2% de $201 = $4.02 de descuento -> $196.98 + IVA = $228.50
    assert venta["descuento"] == 4.02
    assert venta["total"] == 228.5


def test_cliente_no_vip_no_recibe_extra_aunque_pase_de_200():
    _alta_producto()
    venta = gestor.registrar_venta("A1", 201, "ABC001")
    assert venta["descuento"] == 0
    assert venta["total"] == 233.16


def test_cotizar_no_aplica_descuento_vip():
    _alta_producto()
    estimado = gestor.cotizar("A1", 201)
    venta_sin_cliente = gestor.registrar_venta("A1", 201)
    venta_vip = gestor.registrar_venta("A1", 201, "VIP001")
    # la cotizacion equivale a una venta sin cliente, no a la venta VIP
    assert estimado == venta_sin_cliente["total"] == 233.16
    assert venta_vip["total"] == 228.5
    assert estimado != venta_vip["total"]


# ---------------------------------------------------------------------------
# Textos de ultimo_error en registrar_venta (y su orden de validacion)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("codigo", ["", None])
def test_error_codigo_vacio(codigo):
    _alta_producto()
    assert gestor.registrar_venta(codigo, 1) is None
    assert gestor.ultimo_error == "codigo vacio"


def test_error_producto_inexistente():
    _alta_producto()
    assert gestor.registrar_venta("ZZZ", 1) is None
    assert gestor.ultimo_error == "producto no existe"


@pytest.mark.parametrize("cantidad", [0, -2, None])
def test_error_cantidad_invalida(cantidad):
    _alta_producto()
    assert gestor.registrar_venta("A1", cantidad) is None
    assert gestor.ultimo_error == "cantidad invalida"


def test_error_stock_insuficiente():
    _alta_producto(stock=2)
    assert gestor.registrar_venta("A1", 3) is None
    assert gestor.ultimo_error == "stock insuficiente"


def test_orden_de_validacion_codigo_vacio_antes_que_producto_y_cantidad():
    _alta_producto()
    assert gestor.registrar_venta("", 0) is None
    assert gestor.ultimo_error == "codigo vacio"


def test_orden_de_validacion_producto_inexistente_antes_que_cantidad():
    _alta_producto()
    assert gestor.registrar_venta("ZZZ", 0) is None
    assert gestor.ultimo_error == "producto no existe"


def test_orden_de_validacion_cantidad_antes_que_stock():
    _alta_producto(stock=0)
    assert gestor.registrar_venta("A1", 0) is None
    assert gestor.ultimo_error == "cantidad invalida"
