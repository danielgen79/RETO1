"""Configuracion compartida de las pruebas adicionales.

Replica tests/conftest.py (que no se modifica) para poder correr esta carpeta
de forma independiente.
"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import pytest  # noqa: E402

import gestor  # noqa: E402


@pytest.fixture(autouse=True)
def sistema_limpio():
    """Deja el sistema sin datos antes y despues de cada prueba."""
    gestor.reiniciar_sistema()
    yield
    gestor.reiniciar_sistema()
