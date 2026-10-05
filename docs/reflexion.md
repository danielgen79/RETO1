# Reflexión final

## 1. Qué técnicas de prompting funcionaron mejor

El pedir cambios o refactorización 1 a la vez, no englobar en querer hacer todo en un
sólo prompt.

Que el prompt debe ser muy explícito y acotado a la corrección requerida

El llevar un control de los cambios a aplicar, revisar antes de que los aplicara para
validar el cambio, que no se modificaran otras cosas.

## 2. Qué no funcionó o tuve que corregir

Para el `.claudeignore` la petición fue vaga y la propuesta incluía excluir los
datos generados por la app. Con una lista explícita de patrones, y aclarando que
`datos_ejemplo.json` y `docs/evidencia` no debían excluirse, salió bien: si dejo un
criterio abierto, la IA lo rellena con una suposición razonable pero distinta de la mía.

El `CLAUDE.md` que generó `/init` copió del README el comando `cd src && python main.py`.
Al probar la app manualmente en la refactorización #3 vi que así arranca sin datos,
porque `main.py` busca `datos_ejemplo.json` en el directorio actual y está en la raíz.
Lo corregí a `python src/main.py`.

## 3. Qué detectó la IA que yo no había notado

En la #4 la IA advirtió que `calcular_descuento_volumen` debía devolver `0` entero y no
`0.0` cuando no hay descuento. A simple vista es lo mismo, pero el valor se guarda en
el JSON y habría cambiado el comportamiento.

En la #5 explicó dos diferencias que introducía mi refactorización, con una cantidad `NaN` 
y con un `cliente` que no es texto; ninguna ocurre en la app real y las documenté en lugar 
de descubrirlas después.


## 4. Qué aprendí sobre refactorizar con IA

Es un método más seguro para realizar cambios en el código, llevas el control y queda
evidencia de los cambios que se van implementando.

Es más rápido que hacerlo manualmente, tal vez la revisión, codificación y pruebas de los
cambios al código hubiera llevado días en hacerlo, con la IA fue en algunas pocas horas.

## 5. Qué haría diferente

Mejorar los prompts desde el principio, tal vez para proyectos pequeños como este, ejecutar
los cambios en modo automático ya que no recuerdo haber denegado algún cambio propuesto. 
Aunque esto funcionaría únicamente teniendo los tests adicionales necesarios.

