# Archivo D-7

Registro comunitario del mundo del juego. Todos los jugadores exploran el mismo mundo,
generado a partir de una única semilla, así que lo que uno encuentra en un sector
cualquiera está también en la partida de todos los demás. Este repositorio es donde se
anota.

Web publicada: `https://USUARIO.github.io/archivo-d7/`

## Cómo funciona

```
fichas/          el contenido: un fichero de texto por ficha
plantillas/      modelos para copiar al escribir una ficha nueva
build/build.py   genera index.html a partir de fichas/
build/plantilla.html   la web (estética y comportamiento), sin datos
index.html       generado, NO lo edites a mano: se sobrescribe
```

En cada commit a `main`, GitHub ejecuta `build/build.py`, regenera `index.html` y publica
el sitio. No hay servidor, ni base de datos, ni nada que mantener: la web publicada es un
solo fichero estático.

## Para añadir una ficha

Lee [CONTRIBUTING.md](CONTRIBUTING.md). Resumen: creas un `.md` en la carpeta que toque
copiando una plantilla, y abres una pull request. O rellenas el formulario de *Issues* si
prefieres no tocar ficheros.

## Para probarlo en tu ordenador

Solo hace falta Python 3:

```
python3 build/build.py
```

Y abres `index.html` en el navegador.

## Licencia

Textos e imágenes bajo [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/deed.es).
El código del generador, bajo MIT.
