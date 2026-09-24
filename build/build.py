#!/usr/bin/env python3
"""
Construye index.html a partir de las fichas de la carpeta fichas/.

No hace falta instalar nada: solo Python 3. Se ejecuta solo en cada commit
(ver .github/workflows/publicar.yml), pero tambien puedes lanzarlo a mano:

    python3 build/build.py

Cada ficha es un fichero .md con una cabecera de campos entre lineas de ---
y despues el texto. El script lee todas, las ordena y las incrusta en la
plantilla build/plantilla.html, que es la web con la estetica de archivo.
"""

import json
import os
import re
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FICHAS = os.path.join(RAIZ, "fichas")
PLANTILLA = os.path.join(RAIZ, "build", "plantilla.html")
SALIDA = os.path.join(RAIZ, "index.html")

# Carpetas del archivo, en el orden en que salen en la web.
# columnas: [titulo de la columna, campo de la cabecera de la ficha]
# La ultima columna siempre es el estado; el script la añade solo.
CARPETAS = [
    {
        "id": "niveles",
        "nombre": "NIVELES",
        "columnas": [
            ["Designación", "designacion"],
            ["Nombre vulgar", "nombre"],
            ["Profundidad", "profundidad"],
            ["Registrado", "registrado"],
        ],
    },
    {
        "id": "entidades",
        "nombre": "ENTIDADES",
        "columnas": [
            ["Designación", "designacion"],
            ["Nombre vulgar", "nombre"],
            ["Clase", "clase"],
            ["Primer avistamiento", "primer_avistamiento"],
        ],
    },
    {
        "id": "informes",
        "nombre": "INFORMES DE CAMPO",
        "columnas": [
            ["Referencia", "designacion"],
            ["Autor", "autor"],
            ["Nivel", "nivel"],
            ["Sector", "sector"],
        ],
    },
    {
        "id": "fotografias",
        "nombre": "FOTOGRAFÍAS",
        "columnas": [
            ["Archivo", "designacion"],
            ["Nivel", "nivel"],
            ["Sector", "sector"],
            ["Semilla", "semilla"],
        ],
    },
    {
        "id": "sectores",
        "nombre": "SECTORES",
        "columnas": [
            ["Sector", "designacion"],
            ["Niveles registrados", "niveles_registrados"],
            ["Accesos conocidos", "accesos"],
            ["Cobertura", "cobertura"],
        ],
    },
    {
        "id": "protocolos",
        "nombre": "PROTOCOLOS",
        "columnas": [
            ["Referencia", "designacion"],
            ["Asunto", "nombre"],
            ["Obligatorio", "obligatorio"],
            ["Revisión", "revision"],
        ],
    },
]

# Campos que tienen un papel fijo y por eso no se repiten en la lista de
# datos del expediente.
RESERVADOS = {"designacion", "nombre", "estado", "sello", "nota", "firma", "orden"}

ESTADOS = {
    "verificado": ("VERIFICADO", "ver"),
    "disputa": ("EN DISPUTA", "dis"),
    "sin-verificar": ("SIN VERIFICAR", "sin"),
    "sin-confirmar": ("SIN CONFIRMAR", "sin"),
    "sin-explorar": ("SIN EXPLORAR", "sin"),
}


def aviso(msg):
    print("  aviso: " + msg, file=sys.stderr)


def leer_ficha(ruta):
    """Separa la cabecera de campos del cuerpo de texto."""
    with open(ruta, encoding="utf-8") as f:
        texto = f.read()

    if not texto.lstrip().startswith("---"):
        raise ValueError("falta la cabecera: el fichero debe empezar con una linea ---")

    texto = texto.lstrip()
    fin = texto.find("\n---", 3)
    if fin == -1:
        raise ValueError("la cabecera no se cierra: falta la segunda linea ---")

    cabecera_txt = texto[3:fin]
    cuerpo = texto[fin + 4 :].strip()

    campos = []
    for linea in cabecera_txt.splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        if ":" not in linea:
            raise ValueError("linea sin dos puntos en la cabecera: " + linea)
        clave, valor = linea.split(":", 1)
        campos.append((clave.strip(), valor.strip()))
    return campos, cuerpo


def escapar(s):
    return (
        str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    )


def cuerpo_html(cuerpo):
    """
    Convierte el texto de la ficha en parrafos.
      - una linea en blanco separa parrafos
      - **negrita**
      - [[algo]] sale tachado en negro, como un censurado
    """
    parrafos = []
    for bloque in re.split(r"\n\s*\n", cuerpo):
        bloque = bloque.strip()
        if not bloque:
            continue
        html = escapar(bloque.replace("\n", " "))
        html = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", html)
        html = re.sub(
            r"\[\[(.*?)\]\]",
            lambda m: '<span class="redact">' + ("█" * max(3, len(m.group(1)))) + "</span>",
            html,
        )
        parrafos.append(html)
    return parrafos


def _git(ruta, formato, extra=None):
    orden = ["git", "log", "-1", "--format=" + formato]
    if extra:
        orden += extra
    orden += ["--", ruta]
    try:
        out = subprocess.run(orden, cwd=RAIZ, capture_output=True, text=True, timeout=20)
        return out.stdout.strip()
    except Exception:
        return ""


def fecha_git(ruta):
    """Fecha del ultimo commit que toco la ficha; si no hay git, la del fichero."""
    f = _git(ruta, "%ad", ["--date=format:%d.%m"])
    if f:
        return f
    import time

    return time.strftime("%d.%m", time.localtime(os.path.getmtime(ruta)))


def orden_git(ruta):
    """Marca de tiempo para ordenar los ultimos movimientos."""
    t = _git(ruta, "%at")
    if t.isdigit():
        return int(t)
    return int(os.path.getmtime(ruta))


def main():
    datos = {"root": {"path": "C:\\ARCHIVO\\", "folders": []}}
    expedientes = {}
    movimientos = []
    errores = 0

    for carpeta in CARPETAS:
        cid = carpeta["id"]
        ruta_carpeta = os.path.join(FICHAS, cid)
        filas = []

        nombres = sorted(os.listdir(ruta_carpeta)) if os.path.isdir(ruta_carpeta) else []
        for nombre_fichero in nombres:
            if not nombre_fichero.endswith(".md"):
                continue
            ruta = os.path.join(ruta_carpeta, nombre_fichero)
            try:
                campos, cuerpo = leer_ficha(ruta)
            except ValueError as e:
                aviso("%s/%s: %s" % (cid, nombre_fichero, e))
                errores += 1
                continue

            d = dict(campos)
            designacion = d.get("designacion", "").strip()
            if not designacion:
                aviso("%s/%s: falta el campo designacion" % (cid, nombre_fichero))
                errores += 1
                continue

            clave_estado = d.get("estado", "sin-verificar").strip().lower()
            if clave_estado not in ESTADOS:
                aviso(
                    "%s/%s: estado '%s' desconocido, se usa sin-verificar (validos: %s)"
                    % (cid, nombre_fichero, clave_estado, ", ".join(sorted(ESTADOS)))
                )
                clave_estado = "sin-verificar"
            etiqueta, clase = ESTADOS[clave_estado]

            fid = os.path.splitext(nombre_fichero)[0]
            celdas = [d.get(k, "—") or "—" for _, k in carpeta["columnas"]]
            celdas.append(etiqueta)
            filas.append({"id": fid, "c": celdas, "st": clase})

            # Datos del expediente: todo lo de la cabecera menos lo reservado,
            # en el mismo orden en que esta escrito en el fichero.
            lista_campos = [[k, v] for k, v in campos if k not in RESERVADOS]

            expedientes[fid] = {
                "titulo": d.get("nombre", designacion),
                "desig": designacion,
                "stamp": d.get("sello", etiqueta),
                "campos": lista_campos,
                "cuerpo": cuerpo_html(cuerpo),
                "nota": d.get("nota", ""),
                "firma": d.get("firma", ""),
            }

            fecha = fecha_git(ruta)
            movimientos.append(
                {
                    "ts": orden_git(ruta),
                    "d": fecha or "—",
                    "t": "%s · %s" % (designacion, d.get("nombre", "sin nombre")),
                    "go": {"id": cid, "file": fid},
                }
            )

        columnas = [c[0] for c in carpeta["columnas"]] + ["Estado"]
        datos[cid] = {
            "nm": carpeta["nombre"],
            "path": "C:\\ARCHIVO\\" + carpeta["nombre"] + "\\",
            "cols": columnas,
            "rows": filas,
        }
        datos["root"]["folders"].append(
            {
                "id": cid,
                "nm": carpeta["nombre"],
                "ct": "%d ficha%s" % (len(filas), "" if len(filas) == 1 else "s"),
            }
        )
        print("  %-14s %d ficha(s)" % (carpeta["nombre"], len(filas)))

    movimientos.sort(key=lambda m: m["ts"], reverse=True)
    recientes = [{k: m[k] for k in ("d", "t", "go")} for m in movimientos[:6]]

    with open(PLANTILLA, encoding="utf-8") as f:
        plantilla = f.read()

    bloque = (
        "var DATA = " + json.dumps(datos, ensure_ascii=False, indent=2) + ";\n\n"
        "  var FILES = " + json.dumps(expedientes, ensure_ascii=False, indent=2) + ";\n\n"
        "  var RECENT = " + json.dumps(recientes, ensure_ascii=False, indent=2) + ";\n\n"
        "  var ORDER = " + json.dumps([c["id"] for c in CARPETAS]) + ";"
    )

    if "/*__DATOS__*/" not in plantilla:
        print("error: la plantilla no tiene la marca /*__DATOS__*/", file=sys.stderr)
        return 1

    with open(SALIDA, "w", encoding="utf-8") as f:
        f.write(plantilla.replace("/*__DATOS__*/", bloque))

    total = sum(len(datos[c["id"]]["rows"]) for c in CARPETAS)
    print("\n  index.html generado con %d ficha(s)." % total)
    if errores:
        # Una ficha mal escrita no puede tumbar la publicacion del resto: se avisa
        # aqui y en el registro de la accion, pero la web sale igual.
        print(
            "  %d ficha(s) con errores: NO se han incluido en la web. Revisalas."
            % errores,
            file=sys.stderr,
        )
    if total == 0:
        print("error: no se ha podido construir ninguna ficha.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
