# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Contexto

Reto de "Refactorización Asistida por IA": app de consola en Python (3.10+) para inventario y ventas de la tienda "La Esquina". El programa **funciona y todas las pruebas pasan**; el código tiene malas prácticas a propósito y la tarea es mejorarlo **sin cambiar su comportamiento observable**. La entrega es un PR (`refactorizacion` → `main`) con commits atómicos (uno por refactorización), la bitácora en `docs/bitacora.md` y la reflexión final en `docs/reflexion.md`. La bitácora sigue `BITACORA_TEMPLATE.md`: una fila por refactorización con prompt, cambio, justificación y resultado de tests. La evidencia (salidas de pytest y ruff) va en `docs/evidencia/`. Se piden ≥5 refactorizaciones significativas, hechas una a la vez.

## Comandos

Usar el venv del repo (`.venv`). **Ejecutar todo como módulo de Python** (`python -m ...`), nunca los `.exe` del venv: en esta máquina Device Guard bloquea los ejecutables de `.venv\Scripts`, así que `pytest`, `ruff` o `pip` a secas fallan.

```bash
python -m pip install -r requirements.txt            # dependencias (pytest, ruff)
python -m pytest -v tests tests_adicionales          # suite completa (tests originales + adicionales)
python -m pytest -v tests/test_gestor.py::nombre     # una sola prueba
python -m ruff check src                             # linter; ya esta en 0 errores, mantenerlo asi
python src/main.py                                   # app interactiva; desde la raiz (busca datos_ejemplo.json en el cwd)
```

Ejecutar `python -m pytest -v tests tests_adicionales` **y** `python -m ruff check src` después de CADA refactorización.

## Reglas inamovibles

- **No modificar `tests/` ni `pyproject.toml`** (ni relajar reglas de ruff para "pasar" el linter). Los tests son de caja negra: si fallan, el refactor cambió el comportamiento.
- `tests/` no se modifica, pero `tests_adicionales/` sí se puede ampliar: contiene pruebas de caracterización de casos límite (umbrales de descuento, límite VIP, textos de `ultimo_error`) y su propio `conftest.py`. Si una de ellas falla tras un refactor, el comportamiento cambió: no ajustar el test para que pase.
- El comportamiento observable debe quedar idéntico: textos de tickets/reportes/mensajes, redondeos, valores de `ultimo_error`, valores de retorno (`None`/`False`/`True`).
- `agregarProducto` y `buscarProducto` conservan su nombre (los usan los tests); `pyproject.toml` las exime de `pep8-naming`. El resto sí debe ser snake_case.
- Ruff selecciona E, W, F, I, N, B, SIM, UP, C90 (mccabe `max-complexity = 10`, línea de 88 cols); cada regla corresponde a un smell real del proyecto. `python -m ruff check src` está en 0 errores y debe mantenerse así: no introducir errores nuevos.

## Flujo de trabajo por refactorización

- Una sola refactorización por petición; no adelantes otras aunque las veas.
- Antes de renombrar o borrar cualquier función o variable, busca con grep si se usa en `tests/` o en otros módulos.
- Al terminar, ejecuta `python -m pytest -v tests tests_adicionales` y `python -m ruff check src` y muestra el resumen.
- No hagas commit: el usuario revisa el diff y lo hace él.
- Si un test falla, revierte el cambio y explica la causa en vez de forzar una solución.

## Convenciones

- PEP 8 y `snake_case`; nombres de dominio en español (`producto`, `venta`, `folio`).
- Type hints en funciones nuevas o modificadas, con sintaxis 3.10+ (`str | None`, `list[dict]`).
- Docstrings breves en español.
- Constantes en MAYÚSCULAS en lugar de números mágicos (IVA, umbrales de descuento, stock bajo).

Ejemplo de estilo esperado (`hayArchivo` en `almacen.py`):

```python
# antes
def hayArchivo(ruta):
    # checa si ya existe el archivo de datos
    if os.path.exists(ruta):
        return True
    else:
        return False

# después
def hay_archivo(ruta: str) -> bool:
    """Indica si ya existe el archivo de datos."""
    return os.path.exists(ruta)
```

## Arquitectura

Cuatro módulos en `src/`, importados por nombre plano (`import gestor`; no es paquete). `tests/conftest.py` y `tests_adicionales/conftest.py` meten `src/` en `sys.path`.

- `gestor.py`: lógica de negocio y **dueño del estado global**: `INVENTARIO` (dict código→producto), `VENTAS` (lista), `contador_ventas` (folio) y `ultimo_error` (canal de errores: las funciones devuelven `False`/`None` y dejan el motivo ahí; las que lo asignan deben declararlo con `global`). `reiniciar_sistema()` lo resetea (el fixture autouse de conftest lo llama antes/después de cada test). Las reglas de negocio son constantes al inicio del módulo (`TASA_IVA`, umbrales y porcentajes de descuento por volumen, `PREFIJO_CLIENTE_VIP`, `MONTO_MINIMO_VIP`, `DESCUENTO_EXTRA_VIP`).
  - `registrar_venta` ya no es una función gigante: es un flujo corto que orquesta funciones pequeñas: `validar_venta` (guardas en orden: código vacío, producto inexistente, cantidad inválida, stock insuficiente), `calcular_descuento_volumen`, `calcular_descuento_vip`, `calcular_impuesto`, `calcular_total_con_iva` (único punto de redondeo del total) y `armar_ticket`.
  - `cotizar` reutiliza `calcular_descuento_volumen` y `calcular_total_con_iva`, pero **no aplica el descuento VIP** (comportamiento fijado por `tests_adicionales/`) y valida distinto a `registrar_venta` (por ejemplo, un código vacío da "producto no existe").
- `almacen.py`: persistencia JSON (`guardar_datos`, `cargar_datos`, `hay_archivo`); **muta directamente** `gestor.INVENTARIO/VENTAS/contador_ventas/ultimo_error` (acopla ambos módulos). Los `.clear()` + copia mantienen las mismas referencias de dict/lista, así que cualquier refactor debe conservar la identidad de esos objetos (los demás módulos acceden a ellos como `gestor.INVENTARIO`). La clave `"contador"` del JSON es el formato del archivo de datos y no se renombra junto con la variable.
- `reportes.py`: lee el estado de `gestor`; `reporte_inventario` y `resumen_ventas` **imprimen y devuelven** el texto. El umbral de stock bajo es la constante `UMBRAL_STOCK_BAJO`.
- `main.py`: menú interactivo. `menu()` es un ciclo corto que despacha con el diccionario `OPCIONES` (opciones "1" a "7" → una función `opcion_*` por opción); la opción "8" (`opcion_guardar_y_salir`) se atiende aparte porque rompe el ciclo, y cualquier otra imprime "Opcion no valida.". `pedir_codigo_y_cantidad` es el helper de las opciones 2 y 3. No tiene tests: verificar cambios aquí con `snapshot_menu.py` (ver abajo). Nota: `menu()` imprime "Datos cargados" aunque `cargar_datos` falle; es un defecto del original conservado a propósito (ver `docs/bitacora.md`, sección "Hallazgos").

El código muerto original (`calcular_descuento_viejo`, `reporteViejoCSV`, `exportar_txt` comentado, `MODO_DEBUG`) ya se eliminó; no lo reintroduzcas.

Como el ticket de `registrar_venta` no tiene tests, `docs/evidencia/snapshot_ticket.py` sirve para verificar que no cambia: genera el ticket (y el dict de la venta) de 3 ventas de ejemplo (`python docs/evidencia/snapshot_ticket.py <archivo>`); compárese con `docs/evidencia/06_ticket_despues.txt` usando `diff`.

Igual para el menú: `docs/evidencia/snapshot_menu.py` ejecuta `src/main.py` con entradas fijas en 3 escenarios (con copia de `datos_ejemplo.json`, sin archivo y con archivo corrupto) dentro de carpetas temporales, sin modificar el `datos_ejemplo.json` original (`python docs/evidencia/snapshot_menu.py <archivo>`); compárese con `docs/evidencia/09_menu_despues.txt` usando `diff`.
