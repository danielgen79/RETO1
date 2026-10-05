# -*- coding: utf-8 -*-
"""Modulo principal del gestor de inventario y ventas de "La Esquina".

Aqui vive casi toda la logica del negocio. Historicamente este archivo
lo fueron parchando varias personas, asi que hay de todo un poco.
"""

from datetime import datetime

# ---------------------------------------------------------------
# Reglas de negocio: impuestos y descuentos
# ---------------------------------------------------------------
TASA_IVA = 0.16
UMBRAL_DESCUENTO_ALTO = 1000
DESCUENTO_ALTO = 0.10
UMBRAL_DESCUENTO_MEDIO = 500
DESCUENTO_MEDIO = 0.05
PREFIJO_CLIENTE_VIP = "VIP"
MONTO_MINIMO_VIP = 200
DESCUENTO_EXTRA_VIP = 0.02

# ---------------------------------------------------------------
# Estado global de la aplicacion (inventario, ventas y contadores)
# ---------------------------------------------------------------
INVENTARIO = {}
VENTAS = []
contador_ventas = 0
ultimo_error = ""


def reiniciar_sistema():
    """Borra todo el estado del sistema (inventario, ventas y folios)."""
    global contador_ventas, ultimo_error
    INVENTARIO.clear()
    VENTAS.clear()
    contador_ventas = 0
    ultimo_error = ""


def agregarProducto(codigo, nombre, precio, stock):
    # valida los datos y da de alta un producto en el inventario
    global ultimo_error
    if codigo is None or codigo == "":
        ultimo_error = "codigo vacio"
        return False
    if codigo in INVENTARIO:
        ultimo_error = "el producto ya existe"
        return False
    if precio <= 0:
        ultimo_error = "precio invalido"
        return False
    if stock < 0:
        ultimo_error = "stock invalido"
        return False
    x = {}
    x["codigo"] = codigo
    x["nombre"] = nombre
    x["precio"] = precio
    x["stock"] = stock
    INVENTARIO[codigo] = x
    return True


def eliminar_producto(codigo):
    """Quita un producto del inventario. Regresa False si no existe."""
    global ultimo_error
    if codigo in INVENTARIO:
        del INVENTARIO[codigo]
        return True
    ultimo_error = "producto no existe"
    return False


def actualizar_stock(codigo, cantidad):
    """Suma unidades al stock (o resta si la cantidad es negativa)."""
    global ultimo_error
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return False
    aux = INVENTARIO[codigo]["stock"] + cantidad
    if aux < 0:
        ultimo_error = "el stock no puede quedar negativo"
        return False
    INVENTARIO[codigo]["stock"] = aux
    return True


def buscarProducto(texto):
    # busca productos cuyo nombre contenga el texto (sin importar mayusculas)
    temp2 = []
    for k in INVENTARIO:
        if texto.lower() in INVENTARIO[k]["nombre"].lower():
            temp2.append(INVENTARIO[k])
    return temp2


def calcular_descuento_volumen(subtotal: float) -> float:
    """Descuento por volumen de compra segun el subtotal."""
    if subtotal >= UMBRAL_DESCUENTO_ALTO:
        return subtotal * DESCUENTO_ALTO
    if subtotal >= UMBRAL_DESCUENTO_MEDIO:
        return subtotal * DESCUENTO_MEDIO
    return 0


def calcular_impuesto(base: float) -> float:
    """IVA que se cobra sobre la base (subtotal ya con descuento)."""
    return base * TASA_IVA


def calcular_total_con_iva(base: float) -> float:
    """Total redondeado a 2 decimales: la base mas su IVA."""
    return round(base + calcular_impuesto(base), 2)


def validar_venta(codigo: str | None, cantidad: int | None) -> dict | None:
    """Valida la venta; regresa el producto o None (motivo en ultimo_error)."""
    global ultimo_error
    if codigo is None or codigo == "":
        ultimo_error = "codigo vacio"
        return None
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return None
    if cantidad is None or cantidad <= 0:
        ultimo_error = "cantidad invalida"
        return None
    if INVENTARIO[codigo]["stock"] < cantidad:
        ultimo_error = "stock insuficiente"
        return None
    return INVENTARIO[codigo]


def calcular_descuento_vip(
    cliente: str | None, subtotal: float, descuento: float
) -> float:
    """Descuento extra VIP si la compra, ya con descuento, pasa del minimo."""
    if (
        cliente is not None
        and cliente.startswith(PREFIJO_CLIENTE_VIP)
        and subtotal - descuento > MONTO_MINIMO_VIP
    ):
        return subtotal * DESCUENTO_EXTRA_VIP
    return 0


def armar_ticket(venta: dict, hay_descuento: bool) -> str:
    """Arma el ticket en texto plano a partir del registro de la venta."""
    ticket = ""
    ticket = ticket + "TIENDA LA ESQUINA\n"
    ticket = ticket + "----------------------------\n"
    ticket = ticket + "Folio: " + str(venta["folio"]) + "\n"
    ticket = ticket + venta["nombre"] + " x" + str(venta["cantidad"]) + "\n"
    ticket = ticket + "Subtotal: $" + str(venta["subtotal"]) + "\n"
    if hay_descuento:
        ticket = ticket + "Descuento: -$" + str(venta["descuento"]) + "\n"
    ticket = ticket + "IVA: $" + str(venta["impuesto"]) + "\n"
    ticket = ticket + "TOTAL: $" + str(venta["total"]) + "\n"
    return ticket


def registrar_venta(
    codigo: str | None, cantidad: int | None, cliente: str | None = ""
) -> dict | None:
    """Registra una venta completa.

    Valida los datos, calcula descuentos e impuestos, descuenta el stock,
    genera el folio y guarda el registro. Si algo falla regresa None y deja
    el motivo en ultimo_error.
    """
    global contador_ventas
    producto = validar_venta(codigo, cantidad)
    if producto is None:
        return None
    # calculo del subtotal
    subtotal = producto["precio"] * cantidad
    # descuentos por volumen de compra, mas el extra de clientes VIP
    descuento = calcular_descuento_volumen(subtotal)
    descuento = descuento + calcular_descuento_vip(cliente, subtotal, descuento)
    base = subtotal - descuento
    impuesto = calcular_impuesto(base)
    total = calcular_total_con_iva(base)
    # descontar del inventario
    producto["stock"] = producto["stock"] - cantidad
    contador_ventas = contador_ventas + 1
    venta = {}
    venta["folio"] = contador_ventas
    venta["codigo"] = codigo
    venta["nombre"] = producto["nombre"]
    venta["cantidad"] = cantidad
    venta["subtotal"] = round(subtotal, 2)
    venta["descuento"] = round(descuento, 2)
    venta["impuesto"] = round(impuesto, 2)
    venta["total"] = total
    venta["cliente"] = cliente
    venta["fecha"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    venta["ticket"] = armar_ticket(venta, descuento > 0)
    VENTAS.append(venta)
    return venta


def cotizar(codigo, cantidad):
    """Calcula cuanto costaria una compra sin registrar la venta."""
    global ultimo_error
    if codigo not in INVENTARIO:
        ultimo_error = "producto no existe"
        return None
    if cantidad is None or cantidad <= 0:
        ultimo_error = "cantidad invalida"
        return None
    aux = INVENTARIO[codigo]["precio"] * cantidad
    desc = calcular_descuento_volumen(aux)
    base = aux - desc
    return calcular_total_con_iva(base)
