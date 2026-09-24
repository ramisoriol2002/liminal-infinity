# Cómo añadir una ficha

Hay dos formas. Elige la que te resulte menos incómoda; las dos acaban en el mismo sitio.

## La rápida: abrir una propuesta

Ve a la pestaña **Issues** → *New issue* → *Proponer una ficha*, rellena el formulario
y envíalo. No hace falta saber nada de git. Alguien del archivo lo pasará a ficha.

## La directa: escribir la ficha tú

Cada ficha es un fichero de texto en `fichas/`. Para crear una:

1. Abre la carpeta que toque: `fichas/niveles/`, `fichas/entidades/`, `fichas/sectores/`,
   `fichas/informes/` o `fichas/fotografias/`.
2. Botón **Add file** → *Create new file*.
3. Nombre del fichero: la designación en minúsculas y con guiones, terminado en `.md`.
   Ejemplos: `lvl-031.md`, `ent-b-14.md`, `sec-14--3.md`.
4. Copia dentro la plantilla que corresponda de la carpeta `plantillas/` y rellénala.
5. Abajo, **Commit changes** → marca *Create a new branch and start a pull request*.

En dos o tres minutos desde que se acepta, la ficha está publicada en la web.

## La cabecera de la ficha

Es la parte entre las dos líneas de `---`. Son pares `campo: valor`, uno por línea.

Hay cuatro campos con un papel fijo:

| Campo | Para qué sirve |
| --- | --- |
| `designacion` | Obligatorio. Es el identificador: `LVL-031`, `ENT-A-03`, `(14, −3)`. |
| `nombre` | El nombre vulgar, el que usa la gente. |
| `estado` | `verificado`, `disputa`, `sin-verificar`, `sin-confirmar` o `sin-explorar`. |
| `nota` y `firma` | El recuadro de aviso y la línea del pie. |

**Todos los demás campos que escribas salen en el expediente**, en el mismo orden en que
los pongas. Si tu nivel tiene algo que los otros no tienen, inventa el campo y ya está:

```
Temperatura del agua: templada, no baja con la profundidad
```

Algunos campos en minúscula (`profundidad`, `clase`, `sector`, `cobertura`…) se usan
además para rellenar las columnas del índice. Están en `build/build.py`, al principio,
si quieres ver cuáles.

## El texto

Debajo de la cabecera. Una línea en blanco separa párrafos. Dos cosas más:

- `**así**` sale en negrita.
- `[[así]]` sale tachado en negro, como un censurado.

## La regla que no se negocia

**PR-01.** Una ficha pasa a `verificado` cuando dos personas distintas aportan una
captura del mismo sitio con la semilla del mundo y el sector legibles en la imagen.

Sin eso la ficha entra igual, pero marcada. No se borra nada: una ficha en disputa
a la vista vale más que un hueco.

## Licencia

Al aportar aceptas que tu texto se publique bajo **CC BY-SA 4.0**: cualquiera puede
reutilizarlo citando la fuente y manteniendo la misma licencia. Es la licencia que usan
las wikis, y es lo que permite que el archivo siga existiendo si mañana yo desaparezco.
