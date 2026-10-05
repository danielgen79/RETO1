# Bitácora de refactorización

**Nombre:Daniel Vanegas Sánchez
**Matrícula:**
**Fecha:** 2026-10-05

Registra aquí **cada refactorización** que realices con Claude Code. Copia el
prompt tal cual lo escribiste (o un resumen fiel si fue una conversación larga),
describe el cambio que se aplicó al código y justifica por qué mejora la calidad.
Después de cada cambio ejecuta `python -m pytest -v` y anota el resultado.

> En esta máquina Device Guard bloquea los `.exe` del venv, por eso todos los
> comandos se ejecutan como módulo (`python -m pytest -v`, `python -m ruff check src`).

## Fase 0: configuración

Estado inicial: 20 pruebas pasando y 20 errores de ruff (evidencia en
`docs/evidencia/00_tests_inicial.txt` y `docs/evidencia/00_ruff_inicial.txt`).

| Paso | Prompt usado | Resultado | Observaciones |
|------|--------------|-----------|---------------|
| Cambio de modelo | `/model Sonnet` | Modelo establecido en Sonnet 5.5 y guardado como predeterminado. | Comando local: no se le envió ninguna petición al modelo. |
| `/init` | `/init` (prompt estándar de Claude Code: analizar el código y crear un `CLAUDE.md` con comandos y arquitectura). | Se creó `CLAUDE.md` con contexto, comandos, reglas inamovibles, arquitectura y código muerto conocido. | Commit `d1867e9`. Claude verificó con grep que ningún test usaba el código muerto antes de anotarlo. |
| Ajuste de `CLAUDE.md` | "Antes de crear el .claudeignore, actualiza CLAUDE.md con estos cambios, sin tocar ningún otro archivo: 1. En "Comandos": en esta máquina Device Guard bloquea los .exe del venv, así que TODOS los comandos deben ejecutarse como módulo: `python -m pytest -v`, `python -m ruff check src`, `python -m pip ...`. Reemplaza los comandos actuales y agrega una nota explicando por qué. Elimina la línea de `ruff check --fix`. 2. Ya renombré la rama a `refactorizacion`, como pide el README; déjalo así. 3. La bitácora va en `docs/bitacora.md` y la reflexión en `docs/reflexion.md` (lo pide el formato de entrega del curso), siguiendo la plantilla BITACORA_TEMPLATE.md. La evidencia (salidas de tests y ruff) va en `docs/evidencia/`. 4. Agrega una sección "Flujo de trabajo por refactorización": una sola refactorización por petición; no adelantes otras aunque las veas; antes de renombrar o borrar cualquier función o variable, busca con grep si se usa en tests/ o en otros módulos; al terminar, ejecuta `python -m pytest -v` y `python -m ruff check src` y muestra el resumen; no hagas commit: yo reviso el diff y hago el commit; si un test falla, revierte el cambio y explica la causa en vez de forzar una solución. 5. Agrega una sección "Convenciones": PEP 8, snake_case, type hints en funciones nuevas o modificadas (sintaxis 3.10+: `str \| None`, `list[dict]`), docstrings breves en español, nombres de dominio en español (producto, venta, folio), constantes en MAYÚSCULAS en lugar de números mágicos (ej. IVA, umbrales de descuento, stock bajo). 6. Agrega un ejemplo corto "antes → después" de estilo esperado, usando `hayArchivo` de almacen.py. Muéstrame el diff antes de guardar." | Claude mostró el diff propuesto y, tras mi confirmación ("Si guardalo"), lo aplicó solo a `CLAUDE.md`. | Commit `6cf7765`. Pedir el diff antes de guardar permitió revisar los cambios. Problema de Device Guard: resuelto documentando y usando siempre `python -m ...`. |
| `.claudeignore` | "No, créalo así: excluye .venv/, venv/, \_\_pycache\_\_/, \*.pyc, .pytest_cache/, .ruff_cache/, .mypy_cache/, .git/, \*.egg-info/, .coverage, htmlcov/, .DS_Store, \_\_MACOSX/ y .env. Agrega un comentario breve por grupo explicando por qué se excluye. No excluyas datos_ejemplo.json (lo usa la app y sirve para entender la estructura de los datos) ni docs/evidencia (es evidencia del reto)." | Se creó `.claudeignore` con los grupos y comentarios pedidos. | Commit `cdc76dc`. La propuesta inicial de Claude incluía excluir los datos generados por la app; con una lista explícita (conservando `datos_ejemplo.json` y `docs/evidencia`) el resultado fue el correcto. |
| Diagnóstico (modo plan) | "Analiza todo el código de src/ y haz un diagnóstico de code smells. Para cada uno indica: archivo y función, tipo de smell (función larga, nombre poco claro, duplicación, condicional complejo, falta de type hints, manejo de errores débil, código muerto, número mágico, acoplamiento por estado global), severidad (alta/media/baja) y qué regla de ruff lo detecta, si aplica. Después propón un orden de refactorizaciones de la más segura a la más riesgosa, indicando para cada una qué tests la protegen. Considera las restricciones de CLAUDE.md. No modifiques nada." | Diagnóstico por módulo (`gestor.py`, `almacen.py`, `reportes.py`, `main.py`) y plan de 9 refactorizaciones ordenadas de menor a mayor riesgo. Guardado en `docs/diagnostico.md`. | Señaló que la suite no cubre los textos de `ultimo_error`, el ticket, `resumen_ventas` ni `main.py`, así que "pytest en verde" no basta para esas partes. |

## Refactorizaciones

| #  | Prompt usado | Cambio realizado | Justificación | Tests OK |
|----|--------------|------------------|---------------|----------|
| 1  | "Refactorización #1 del diagnóstico: eliminar código muerto.<br><br>Elimina: calcular_descuento_viejo y el bloque comentado de exportar_txt en gestor.py, la variable MODO_DEBUG si nadie la usa, la función reporteViejoCSV y el import os sin usar en reportes.py.<br><br>Antes de borrar cada elemento, busca con grep en src/ y tests/ y muéstrame el resultado que demuestra que no se usa. No hagas ningún otro cambio (ni cabeceras coding, ni renombres, ni formato). Al terminar ejecuta python -m pytest -v y python -m ruff check src, y dime cuántos errores de ruff quedan y cuáles desaparecieron." | **Grep previo en `src/` y `tests/`:** solo aparecen las definiciones, sin llamadas: `calcular_descuento_viejo` (`gestor.py:185`), `exportar_txt` (`gestor.py:193`, comentado), `MODO_DEBUG` (`gestor.py:17`), `reporteViejoCSV` (`reportes.py:83`); `os` solo en `import os` (`reportes.py:4`) y sin ningún `os.` en el archivo.<br><br>**Cambios:** en `gestor.py` se eliminaron `MODO_DEBUG`, `calcular_descuento_viejo` y el bloque comentado de `exportar_txt`; en `reportes.py` se eliminaron `reporteViejoCSV` y `import os`. | El código muerto confunde al lector (parece parte de la lógica), no tiene llamadas ni pruebas y, en el caso de `reporteViejoCSV`, arrastraba un `open` sin `with` y un nombre no PEP 8. Borrarlo no cambia el comportamiento observable y reduce la superficie a mantener. | **20/20 pasan.** Ruff: **20 → 17** errores. Desaparecieron `F401` (`os` sin usar), `N802` (`reporteViejoCSV`) y `SIM115` (`open` sin `with` en `reportes.py`). |
| 2  |              |                  |               |          |
| 3  |              |                  |               |          |
| 4  |              |                  |               |          |
| 5  |              |                  |               |          |

> Agrega más filas si realizas más de 5 refactorizaciones.

## Reflexión final (10-15 líneas)

Responde: ¿Qué tan útil fue Claude Code para detectar y corregir los problemas?
¿Qué propuso la IA que tú no habías notado? ¿En qué casos tuviste que corregir
o rechazar sus sugerencias? ¿Qué aprendiste sobre refactorizar con apoyo de IA?

*(Escribe aquí tu reflexión)*
