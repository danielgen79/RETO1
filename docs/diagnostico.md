# Diagnóstico de code smells y orden de refactorizaciones — `src/`

## Contexto

Reto de refactorización: el código de `src/` funciona (la suite pasa) pero ruff reporta 20 errores
(`docs/evidencia/00_ruff_inicial.txt`). Este documento diagnostica los smells y propone un orden de
refactorización de la más segura a la más riesgosa. Solo lectura: no se modificó nada. Restricciones
de CLAUDE.md: no tocar `tests/` ni `pyproject.toml`, comportamiento observable idéntico, conservar
`agregarProducto` / `buscarProducto`, una refactorización por petición, sin commits por mi parte,
comandos como `python -m ...`.

> Las líneas citadas salen de leer los archivos; no ejecuté pytest ni ruff en esta sesión
> (el conteo de 20 errores viene del archivo de evidencia).

## 1. Diagnóstico

### gestor.py

| # | Función / símbolo | Smell | Sev. | Ruff |
|---|---|---|---|---|
| G1 | `registrar_venta` | Función larga: validación, descuentos, VIP, IVA, stock, folio, ticket y registro en una sola | Alta | C901 (12 > 10) |
| G2 | `registrar_venta` (L96-112) | Condicional complejo: validación con 4 `if/else` anidados en pirámide | Alta | — (el anidamiento no lo marca; sí C901 en conjunto) |
| G3 | `registrar_venta` (L126-130) | Condicional complejo: 4 `if` anidados para la regla VIP | Media | SIM102 ×3 |
| G4 | `registrar_venta` (L117-123) | Condicional complejo: `if/else` anidado en vez de `elif`/ternario | Baja | SIM108 |
| G5 | `registrar_venta` / `cotizar` | Duplicación: tabla de descuentos por volumen e IVA copiada en ambas | Alta | — |
| G6 | `registrar_venta`, `cotizar` | Números mágicos: `1000`, `500`, `0.10`, `0.05`, `0.02`, `200`, `0.16`, `"VIP"`/`[0:3]` | Alta | — |
| G7 | `contadorVentas` | Nombre mixedCase + estado global reasignado con `global` | Media | N816 |
| G8 | `INVENTARIO`, `VENTAS`, `ultimo_error` | Acoplamiento por estado global (también lo muta `almacen`) | Alta | — |
| G9 | `temp2`, `aux`, `desc`, `x`, `t`, `d` | Nombres poco claros | Media | — |
| G10 | `agregarProducto` | Construcción de dict en 5 líneas; sin type hints. (Nombre intocable) | Baja | — |
| G11 | `MODO_DEBUG` | Código muerto: constante que nadie usa | Baja | — |
| G12 | `calcular_descuento_viejo`, bloque `exportar_txt` comentado | Código muerto | Media | — |
| G13 | Todo el módulo | Faltan type hints | Media | — (ANN no está activo) |
| G14 | línea 1 | Cabecera `# -*- coding` innecesaria | Baja | UP009 |

### almacen.py

| # | Función | Smell | Sev. | Ruff |
|---|---|---|---|---|
| A1 | `guardar_datos` | Archivo abierto sin `with` | Media | SIM115 |
| A2 | `cargar_datos` | Archivo abierto sin `with`, `close()` duplicado en dos ramas | Media | SIM115, UP015 |
| A3 | `cargar_datos` | Manejo de errores débil: `except Exception` demasiado amplio; `d["inventario"]` y `d["ventas"]` lanzan `KeyError` si el JSON no los trae; solo `ultimo_error` como canal | Media | — (BLE/E722 no activos) |
| A4 | `cargar_datos` | Copia elemento por elemento con `clear()` + bucle (equivale a `update`/`extend`) | Baja | — |
| A5 | `hayArchivo` | Nombre mixedCase + `if/else` que devuelve `True/False` | Media | N802, SIM103 |
| A6 | `guardar_datos`, `cargar_datos` | Acoplamiento por estado global: muta directo `gestor.*` incluido `ultimo_error` | Alta | — |
| A7 | `guardar_datos` | Siempre devuelve `True` (sin manejo de `OSError`); nombres `d`, `f` | Baja | — |
| A8 | línea 1 / módulo | Cabecera coding; sin type hints | Baja | UP009 |

### reportes.py

| # | Función | Smell | Sev. | Ruff |
|---|---|---|---|---|
| R1 | `hacer_cosa` | Nombre poco claro (formatea dinero) | Media | — |
| R2 | `productos_stock_bajo`, `reporte_inventario` | Número mágico `5` duplicado (umbral de stock bajo) | Media | — |
| R3 | `mas_vendidos` | Ordenamiento de burbuja manual + conteo manual (debe ser `Counter`/`sorted`) | Media | — |
| R4 | `reporte_inventario`, `resumen_ventas`, `total_vendido` | Concatenación de strings con `+` y acumuladores a mano; mezcla de formato e impresión (`print` + `return`) | Baja | — |
| R5 | `reporteViejoCSV` | Código muerto + `open` sin `with` + nombre mixedCase | Media | N802, SIM115 |
| R6 | `import os` | Import sin usar | Baja | F401 |
| R7 | nombres `s`, `aux`, `temp`, `t` | Nombres poco claros | Baja | — |
| R8 | módulo | Cabecera coding; sin type hints | Baja | UP009 |

### main.py

| # | Función | Smell | Sev. | Ruff |
|---|---|---|---|---|
| M1 | `menu` | Función larga y condicional complejo: `if/elif` de 8 ramas con E/S mezclada con lógica | Alta | C901 (17 > 10) |
| M2 | `menu` | Nombres crípticos: `op`, `c`, `n`, `p`, `s`, `cant`, `cli`, `v`, `t` | Media | — |
| M3 | `menu` (opciones 1-3) | Duplicación: "pedir código + cantidad + imprimir resultado o `ultimo_error`" repetido | Media | — |
| M4 | `menu` | Acoplamiento al estado global (`gestor.ultimo_error`) | Media | — |
| M5 | imports L4-6 | Imports sin ordenar | Baja | I001 |
| M6 | `pedir_numero`, `menu` | Sin type hints; `temp2` como nombre | Baja | — |
| M7 | línea 1 | Cabecera coding | Baja | UP009 |

**Cobertura de ruff:** los 20 errores se reparten así: UP009 ×4, SIM115 ×3, SIM102 ×3, N802 ×2, C901 ×2,
UP015, SIM103, SIM108, N816, I001, F401. Los smells sin regla (duplicación, números mágicos, estado
global, nombres crípticos, type hints, manejo de errores) son trabajo de refactorización que ruff no
verifica. Como CLAUDE.md prohíbe `--fix`, los ítems "triviales" se aplican a mano.

## 2. Hueco de cobertura de los tests (importante)

La suite protege **cálculos y flujos**, pero **no** protege:

- Los textos de `ultimo_error` (ningún test los compara).
- El formato del ticket de `registrar_venta` ni el texto de `resumen_ventas`.
- `main.py` completo (cero tests), incluida la llamada a `hayArchivo`.
- `eliminar_producto`/`cotizar` con errores, `cargar_datos` con JSON corrupto, `reporteViejoCSV`.
- Orden de validación en `registrar_venta` (código vacío → producto no existe → cantidad → stock).
- Diferencia de comportamiento `cotizar` vs `registrar_venta`: `cotizar` NO aplica descuento VIP
  y para código vacío devuelve "producto no existe" (no "codigo vacio").

Que `pytest` pase **no** prueba que esos puntos se conservaron. Mitigación propuesta: antes de las
refactorizaciones 4, 5 y 7, capturar una "foto" del comportamiento (script desechable en el scratchpad,
no en `tests/`) con entradas representativas y comparar antes/después.

## 3. Orden propuesto (de más segura a más riesgosa)

Una refactorización por petición, con `python -m pytest -v` y `python -m ruff check src` al final de
cada una, y sin commit por mi parte.

| # | Refactorización | Smells | Ruff que elimina | Tests que la protegen | Riesgo |
|---|---|---|---|---|---|
| 1 | **Eliminar código muerto**: `calcular_descuento_viejo`, `exportar_txt` comentado, `reporteViejoCSV`, `MODO_DEBUG`, `import os` de reportes. Antes: grep en `tests/` y `src/` | G11, G12, R5, R6 | F401, N802 (reporteViejoCSV), SIM115 (reportes) | Ninguno los llama; basta que toda la suite siga en verde | Mínimo |
| 2 | **Números mágicos → constantes** (`IVA`, umbrales/porcentajes de descuento, `STOCK_BAJO`, `UMBRAL_VIP`, `PREFIJO_VIP`). Mantener valores y orden exacto de operaciones con floats | G6, R2 | — | `test_venta_sin_descuento_aplica_iva`, `..._volumen_medio`, `..._volumen_alto`, `..._cliente_vip...`, `test_cotizar_coincide...`, `test_stock_bajo_detecta...`, `test_reporte_inventario_marca_stock_bajo` | Bajo (float: no reordenar sumas/productos) |
| 3 | **Persistencia con `with` y `hay_archivo`**: usar context managers, quitar `close()` duplicado, `hayArchivo` → `hay_archivo` (+ llamada en `main.py`), `return os.path.exists(...)` | A1, A2, A5, A7 | SIM115 ×2, UP015, N802, SIM103 | `test_guardar_y_cargar_conserva_los_datos`, `test_el_folio_continua...`, `test_cargar_archivo_inexistente_regresa_false`. Grep previo de `hayArchivo`; `main.py` no tiene tests → verificar a mano | Bajo |
| 4 | **Extraer lógica duplicada de precio**: una función compartida (subtotal → descuento por volumen → base → IVA) usada por `registrar_venta` y `cotizar`. Conservar que `cotizar` no aplica VIP | G5 | — | `test_venta_con_descuento_*`, `test_venta_cliente_vip...`, `test_cotizar_coincide_con_el_total_de_la_venta` | Medio (redondeos: seguir redondeando solo al final, igual que hoy) |
| 5 | **Dividir `registrar_venta`** (validación con cláusulas de guarda en el mismo orden, cálculo de descuento VIP, armado del ticket, registro) y aplanar condicionales; nombres claros y type hints | G1–G4, G9 | C901, SIM102 ×3, SIM108 | Tests de venta (folio, stock, descuentos, VIP, rechazos) y `test_almacen`. **No cubiertos:** textos de error y ticket → comparar con la foto previa | Medio-alto |
| 6 | **`reportes`**: `hacer_cosa` → `formatear_dinero`, `mas_vendidos` con `Counter` + `sorted` (orden estable y desempate idéntico al burbuja), f-strings/`join` | R1, R3, R4, R7 | — | `test_mas_vendidos_ordena_por_unidades`, `test_total_vendido...`, `test_reporte_inventario...`. **No cubierto:** `resumen_ventas` → foto previa | Medio |
| 7 | **Renombrar `contadorVentas` → `contador_ventas`** (gestor + almacen + grep en tests/main) | G7 | N816 | `test_el_folio_continua_despues_de_recargar`, `test_venta_descuenta_stock_y_asigna_folio`. Verificar que ningún test lo referencia por nombre | Medio (un nombre mal cambiado en `almacen` rompería solo la carga del folio) |
| 8 | **Descomponer `menu`** de `main.py`: una función por opción (o tabla de despacho), helper para "código + cantidad", nombres claros, imports ordenados | M1–M6 | C901, I001 | **Ninguno** (main.py sin tests). Mitigación: ejecutar el menú con entradas guionadas antes y después y comparar la salida | Alto por falta de red |
| 9 | **Limpieza final**: cabeceras `# -*- coding`, type hints residuales | G13, G14, A8, M7, R8 | UP009 ×4 | Suite completa | Mínimo |

Con 1–9 se llega a 0 errores de ruff: C901 (5 y 8), N802 (1 y 3), N816 (7), SIM102/SIM108 (5), SIM103/SIM115/UP015 (1 y 3),
F401 (1), I001 (8), UP009 (9).

### Fuera de alcance por riesgo (solo mencionar, no hacer)

- Encapsular el estado global en una clase o pasar el estado por parámetro (G8, A6, M4): los tests
  acceden a `gestor.INVENTARIO`, `gestor.VENTAS` y `gestor.reiniciar_sistema()`, y `conftest.py`
  depende de ellos; cambiarlo obligaría a modificar tests.
- Reemplazar `ultimo_error` por excepciones: cambia el contrato observable (`False`/`None`).
- Endurecer `cargar_datos` (A3) cambiaría qué entradas fallan: solo con acuerdo explícito.

## 4. Verificación (en cada paso futuro)

1. Antes del cambio: `grep` de nombres afectados en `tests/` y `src/`.
2. `python -m pytest -v` (todo en verde) y `python -m ruff check src` (el conteo baja según la columna "Ruff").
3. En los pasos 3, 5, 6 y 8: comparar la foto de comportamiento antes/después.
4. Guardar la salida en `docs/evidencia/` y registrar la fila en `docs/bitacora.md`.
