# Reto: Refactorización Asistida por IA

## Gestor de inventario y ventas — Tienda "La Esquina"

Este repositorio contiene una aplicación de consola en Python para administrar
el inventario y las ventas de una tienda pequeña: alta de productos, registro
de ventas con descuentos e IVA, cotizaciones, alertas de stock bajo, reporte de
más vendidos y persistencia de datos en JSON.

**El programa funciona correctamente** (todas las pruebas pasan), pero el código
fue escrito "al aventón" y arrastra una cantidad importante de malas prácticas:
funciones gigantes que hacen de todo, lógica duplicada, nombres crípticos,
números mágicos, estado global, código muerto, anidamiento excesivo, estilos de
nombrado mezclados... Tu misión es **mejorarlo sin romperlo**, usando Claude
Code como asistente.

### Estructura del proyecto

```
.
├── src/
│   ├── gestor.py        # Lógica de productos y ventas
│   ├── almacen.py       # Carga y guardado de datos (JSON)
│   ├── reportes.py      # Reportes e indicadores
│   └── main.py          # Menú interactivo de consola
├── tests/               # Suite de pruebas (pytest) — NO la modifiques
├── datos_ejemplo.json   # Datos de ejemplo para el menú interactivo
├── requirements.txt
├── pyproject.toml       # Configuración del linter (ruff) — NO la modifiques
└── BITACORA_TEMPLATE.md # Plantilla para tu bitácora de prompts
```

## Instalación y ejecución

Requiere Python 3.10 o superior.

```bash
# 1. Crear y activar un entorno virtual
python -m venv .venv
source .venv/bin/activate        # En Windows: .venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la suite de pruebas (deben pasar TODAS)
pytest

# 4. Ejecutar el linter (al inicio reporta ~20 problemas; al final: 0)
ruff check src

# 5. (Opcional) Probar la aplicación interactiva
cd src && python main.py
```

## Instrucciones del reto

Trabaja en un **fork** de este repositorio y sigue estos pasos:

1. **Configura el proyecto para Claude Code.** Crea un `CLAUDE.md` con el
   contexto del proyecto (qué hace, cómo correr las pruebas, reglas que la IA
   debe respetar — por ejemplo, *no modificar los tests*) y un `.claudeignore`
   con lo que no debe leer (entornos virtuales, cachés, datos generados).
   Crear estos archivos es parte del reto: **no vienen incluidos**.
2. **Explora el código con Claude Code.** Pídele un diagnóstico: qué *code
   smells* detecta y qué refactorizaciones recomienda. Prioriza.
3. **Aplica al menos 5 refactorizaciones significativas**, una a la vez.
   Ejemplos válidos: dividir una función gigante, extraer lógica duplicada,
   renombrar con nombres descriptivos y estilo consistente, reemplazar números
   mágicos por constantes, aplanar condicionales anidados, eliminar código
   muerto, agregar type hints, reducir el estado global, separar lógica de
   entrada/salida. Cambios cosméticos aislados (una línea, un espacio) no
   cuentan como refactorización significativa.
4. **Valida con `pytest` y `ruff check src` después de CADA refactorización.** La suite de
   pruebas es de caja negra: si un cambio la rompe, tu refactorización alteró
   el comportamiento y debes corregirla. **No está permitido modificar los
   tests** para hacerlos pasar.
5. **Documenta cada prompt en la bitácora.** Copia `BITACORA_TEMPLATE.md` a
   `BITACORA.md` y llena una fila por refactorización: prompt usado, cambio
   realizado, justificación y resultado de los tests. Cierra con tu reflexión.
6. **Entrega mediante Pull Request** hacia tu propio repositorio (rama
   `refactorizacion` → `main`), con commits atómicos (idealmente uno por
   refactorización) y la bitácora incluida. Comparte la liga del PR en la
   plataforma del curso.

## Criterios de evaluación

| Criterio | Descripción | Peso |
|----------|-------------|------|
| Configuración | `CLAUDE.md` y `.claudeignore` completos y pertinentes | 15% |
| Calidad de refactorizaciones | ≥5 refactorizaciones significativas, bien elegidas y bien ejecutadas | 30% |
| Tests pasando | La suite completa pasa al final (y después de cada cambio) | 20% |
| Bitácora | Prompts documentados, cambios explicados y justificados | 25% |
| Reflexión | Análisis crítico del trabajo con la IA | 10% |

## Reglas

- No modifiques los archivos de `tests/` ni `pyproject.toml`.
- El código final de `src/` debe pasar `ruff check src` **sin errores**. La
  configuración ya viene incluida en `pyproject.toml`; cada regla corresponde a
  un *code smell* real del proyecto (funciones demasiado complejas, nombres que
  no siguen PEP 8, archivos abiertos sin `with`, imports sin usar, `if`
  anidados…). `ruff check src --fix` corrige solo los triviales: el resto es
  trabajo de refactorización. Las funciones `agregarProducto` y
  `buscarProducto` conservan su nombre porque los tests las usan.
- El comportamiento observable del programa debe mantenerse idéntico.
- Puedes (y debes) usar Claude Code, pero **tú eres responsable** de revisar,
  entender y validar cada cambio que la IA proponga.

## Instalación y ejecución (entrega)

Esta sección describe cómo reproducir el trabajo entregado. Los comandos se
ejecutan desde la **raíz del repositorio**.

### Requisitos previos

- Python 3.10 o superior (probado con Python 3.14).
- pip.
- git.

### 1. Clonar el repositorio y crear el entorno virtual

```bash
git clone -b refactorizacion https://github.com/danielgen79/RETO1.git
cd RETO1

python -m venv .venv
```

Activar el entorno virtual:

```powershell
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (cmd)
.venv\Scripts\activate.bat
```

```bash
# Linux / macOS
source .venv/bin/activate
```

Instalar las dependencias:

```bash
python -m pip install -r requirements.txt
```

### 2. Ejecutar las pruebas

```bash
python -m pytest -v tests tests_adicionales
```

- `tests/` es la suite original del reto y **no se modificó**.
- `tests_adicionales/` contiene pruebas nuevas de casos límite (umbrales de
  descuento por volumen en 500 y 1000, límite del descuento VIP, `cotizar` sin
  descuento VIP y textos exactos de `ultimo_error` con su orden de validación).
  Son pruebas de caracterización: fijan el comportamiento actual para detectar
  cambios accidentales al refactorizar. Tiene su propio `conftest.py` para no
  tocar el de `tests/`.

### 3. Ejecutar el linter

```bash
python -m ruff check src
```

El resultado esperado es `All checks passed!` (0 errores).

### 4. Ejecutar la aplicación

```bash
python src/main.py
```

Ejecútala **desde la raíz del repositorio**. `main.py` busca `datos_ejemplo.json`
en el directorio actual, y ese archivo está en la raíz. El comando original de
este README (`cd src && python main.py`) arranca **sin datos**, porque en `src/`
no existe `datos_ejemplo.json`. La opción 8 del menú guarda los cambios en
`datos_ejemplo.json`.

### Nota sobre Device Guard (Windows)

En equipos donde Device Guard bloquea los `.exe` del entorno virtual (por
ejemplo `pytest.exe`, `ruff.exe` o `pip.exe`), ejecuta siempre las herramientas
como módulo de Python: `python -m pytest`, `python -m ruff` y `python -m pip`,
tal como se muestra en esta sección.

### Scripts de verificación

`main.py` y el ticket de venta no tienen pruebas automáticas, así que
`docs/evidencia/` incluye dos scripts que generan su salida con entradas fijas
para compararla antes y después de un cambio:

```bash
# Ticket de 3 ventas de ejemplo (sin descuento, con volumen y VIP)
python docs/evidencia/snapshot_ticket.py salida_ticket.txt
diff --strip-trailing-cr salida_ticket.txt docs/evidencia/06_ticket_despues.txt

# Menú completo, en 3 escenarios (con datos, sin archivo y con archivo corrupto)
python docs/evidencia/snapshot_menu.py salida_menu.txt
diff --strip-trailing-cr salida_menu.txt docs/evidencia/09_menu_despues.txt
```

- `snapshot_ticket.py` imprime el ticket y el registro de cada venta.
- `snapshot_menu.py` ejecuta `src/main.py` por stdin, siempre en carpetas
  temporales, por lo que **no modifica** el `datos_ejemplo.json` original.
- Si `diff` no muestra diferencias, la salida coincide con la registrada en la
  entrega. En PowerShell puedes usar `fc salida_ticket.txt docs\evidencia\06_ticket_despues.txt`.
