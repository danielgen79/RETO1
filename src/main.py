"""Punto de entrada del gestor de tienda (menu interactivo en consola)."""

import almacen
import gestor
import reportes

ARCHIVO = "datos_ejemplo.json"


def pedir_numero(mensaje: str) -> float:
    """Pide un numero al usuario hasta que escriba algo valido."""
    while True:
        texto = input(mensaje)
        try:
            return float(texto)
        except ValueError:
            print("Eso no es un numero, intenta de nuevo.")


def pedir_codigo_y_cantidad() -> tuple[str, int]:
    """Pide el codigo del producto y la cantidad (opciones 2 y 3)."""
    codigo = input("Codigo del producto: ")
    cantidad = int(pedir_numero("Cantidad: "))
    return codigo, cantidad


def mostrar_menu() -> None:
    """Imprime las opciones del menu."""
    print("")
    print("1) Agregar producto")
    print("2) Registrar venta")
    print("3) Cotizar")
    print("4) Reporte de inventario")
    print("5) Resumen de ventas")
    print("6) Mas vendidos")
    print("7) Alertas de stock bajo")
    print("8) Guardar y salir")


def opcion_agregar_producto() -> None:
    """Opcion 1: da de alta un producto."""
    codigo = input("Codigo: ")
    nombre = input("Nombre: ")
    precio = pedir_numero("Precio: ")
    stock = int(pedir_numero("Stock inicial: "))
    if gestor.agregarProducto(codigo, nombre, precio, stock):
        print("Producto agregado.")
    else:
        print("Error:", gestor.ultimo_error)


def opcion_registrar_venta() -> None:
    """Opcion 2: registra una venta e imprime su ticket."""
    codigo, cantidad = pedir_codigo_y_cantidad()
    cliente = input("Codigo de cliente (enter si no tiene): ")
    venta = gestor.registrar_venta(codigo, cantidad, cliente)
    if venta is not None:
        print(venta["ticket"])
    else:
        print("Error:", gestor.ultimo_error)


def opcion_cotizar() -> None:
    """Opcion 3: cotiza una compra sin registrarla."""
    codigo, cantidad = pedir_codigo_y_cantidad()
    total = gestor.cotizar(codigo, cantidad)
    if total is not None:
        print("Total estimado (con IVA): $" + str(total))
    else:
        print("Error:", gestor.ultimo_error)


def opcion_reporte_inventario() -> None:
    """Opcion 4: muestra el reporte de inventario."""
    reportes.reporte_inventario()


def opcion_resumen_ventas() -> None:
    """Opcion 5: muestra el resumen de ventas."""
    reportes.resumen_ventas()


def opcion_mas_vendidos() -> None:
    """Opcion 6: muestra los productos mas vendidos."""
    for codigo, unidades in reportes.mas_vendidos():
        print(codigo, "->", unidades, "unidades")


def opcion_alertas_stock_bajo() -> None:
    """Opcion 7: avisa de los productos con stock bajo."""
    bajos = reportes.productos_stock_bajo()
    if len(bajos) == 0:
        print("No hay productos con stock bajo.")
    else:
        for producto in bajos:
            print(
                "OJO:", producto["nombre"], "solo tiene", producto["stock"], "unidades"
            )


def opcion_guardar_y_salir() -> None:
    """Opcion 8: guarda los datos y se despide."""
    almacen.guardar_datos(ARCHIVO)
    print("Datos guardados. Hasta luego.")


OPCIONES = {
    "1": opcion_agregar_producto,
    "2": opcion_registrar_venta,
    "3": opcion_cotizar,
    "4": opcion_reporte_inventario,
    "5": opcion_resumen_ventas,
    "6": opcion_mas_vendidos,
    "7": opcion_alertas_stock_bajo,
}


def menu() -> None:
    """Ciclo principal del menu interactivo."""
    print("Bienvenido al gestor de la tienda La Esquina")
    if almacen.hay_archivo(ARCHIVO):
        almacen.cargar_datos(ARCHIVO)
        print("Datos cargados de", ARCHIVO)
    while True:
        mostrar_menu()
        opcion = input("Opcion: ")
        if opcion == "8":
            opcion_guardar_y_salir()
            break
        accion = OPCIONES.get(opcion)
        if accion is None:
            print("Opcion no valida.")
        else:
            accion()


if __name__ == "__main__":
    menu()
