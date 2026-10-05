# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Contexto

Reto de "Refactorización Asistida por IA": app de consola en Python (3.10+) para inventario y ventas de la tienda "La Esquina". El programa **funciona y todas las pruebas pasan**; el código tiene malas prácticas a propósito y la tarea es mejorarlo **sin cambiar su comportamiento observable**. La entrega es un PR (`refactorizacion` → `main`) con commits atómicos (uno por refactorización), la bitácora en `docs/bitacora.md` y la reflexión final en `docs/reflexion.md`. La bitácora sigue `BITACORA_TEMPLATE.md`: una fila por refactorización con prompt, cambio, justificación y resultado de tests. La evidencia (salidas de pytest y ruff) va en `docs/evidencia/`. Se piden ≥5 refactorizaciones significativas, hechas una a la vez.

## Comandos

Usar el venv del repo (`.venv`). **Ejecutar todo como módulo de Python** (`python -m ...`), nunca los `.exe` del venv: en esta máquina Device Guard bloquea los ejecutables de `.venv\Scripts`, así que `pytest`, `ruff` o `pip` a secas fallan.

```bash
python -m pip install -r requirements.txt            # dependencias (pytest, ruff)
python -m pytest -v                                  # suite completa (testpaths = tests)
python -m pytest -v tests/test_gestor.py::nombre     # una sola prueba
python -m ruff check src                             # linter; el objetivo final es 0 errores
cd src && python main.py                             # app interactiva (lee/escribe datos_ejemplo.json en el cwd)
```

Ejecutar `python -m pytest -v` **y** `python -m ruff check src` después de CADA refactorización.

## Reglas inamovibles

- **No modificar `tests/` ni `pyproject.toml`** (ni relajar reglas de ruff para "pasar" el linter). Los tests son de caja negra: si fallan, el refactor cambió el comportamiento.
- El comportamiento observable debe quedar idéntico: textos de tickets/reportes/mensajes, redondeos, valores de `ultimo_error`, valores de retorno (`None`/`False`/`True`).
- `agregarProducto` y `buscarProducto` conservan su nombre (los usan los tests); `pyproject.toml` las exime de `pep8-naming`. El resto sí debe ser snake_case.
- Ruff selecciona E, W, F, I, N, B, SIM, UP, C90 (mccabe `max-complexity = 10`, línea de 88 cols); cada regla corresponde a un smell real del proyecto.

## Flujo de trabajo por refactorización

- Una sola refactorización por petición; no adelantes otras aunque las veas.
- Antes de renombrar o borrar cualquier función o variable, busca con grep si se usa en `tests/` o en otros módulos.
- Al terminar, ejecuta `python -m pytest -v` y `python -m ruff check src` y muestra el resumen.
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

Cuatro módulos en `src/`, importados por nombre plano (`import gestor`; no es paquete). `tests/conftest.py` mete `src/` en `sys.path`.

- `gestor.py`: lógica de negocio y **dueño del estado global**: `INVENTARIO` (dict código→producto), `VENTAS` (lista), `contadorVentas` (folio) y `ultimo_error` (canal de errores: las funciones devuelven `False`/`None` y dejan el motivo ahí). `reiniciar_sistema()` lo resetea (el fixture autouse de conftest lo llama antes/después de cada test). `registrar_venta` es una función gigante (validación, descuento por volumen, extra VIP, IVA 16 %, stock, folio, ticket) y `cotizar` duplica su cálculo de descuento/IVA.
- `almacen.py`: persistencia JSON; **muta directamente** `gestor.INVENTARIO/VENTAS/contadorVentas/ultimo_error` (acopla ambos módulos). Los `.clear()` + copia mantienen las mismas referencias de dict/lista, así que cualquier refactor debe conservar la identidad de esos objetos (los demás módulos acceden a ellos como `gestor.INVENTARIO`).
- `reportes.py`: lee el estado de `gestor`; `reporte_inventario` y `resumen_ventas` **imprimen y devuelven** el texto. Umbral de stock bajo (5) hardcodeado en dos lugares.
- `main.py`: menú interactivo con un `if/elif` largo; mezcla E/S con llamadas a la lógica.

Código muerto conocido: `calcular_descuento_viejo`, `reporteViejoCSV`, bloque comentado `exportar_txt` (verificar con grep que no los use ningún test antes de borrar).
