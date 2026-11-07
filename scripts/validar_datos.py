
import csv
import math
import re
import sys
from datetime import datetime
from pathlib import Path

COLUMNAS = [
    "id", "name", "recclass", "mass (g)",
    "fall", "year", "reclat", "reclong"
]


def obtener_anio(valor):
    """Acepta un año entero o una fecha ISO completa."""
    valor = valor.strip()

    if not valor:
        return None

    if re.fullmatch(r"\d{1,4}", valor):
        anio = int(valor)
    else:
        try:
            # La NASA puede registrar fechas completas.
            fecha = datetime.fromisoformat(
                valor.replace("Z", "+00:00")
            )
            anio = fecha.year
        except ValueError:
            raise ValueError("Formato de año o fecha incorrecto")

    if not 1 <= anio <= 2026:
        raise ValueError("El año debe estar entre 1 y 2026")

    return anio


def validar_numero(valor, campo, minimo, maximo=None):
    """Permite faltantes, pero rechaza números inválidos."""
    valor = valor.strip()

    if not valor:
        return None

    try:
        numero = float(valor)
    except ValueError:
        raise ValueError(f"{campo}: no es un número válido")

    if not math.isfinite(numero):
        raise ValueError(f"{campo}: el número no es finito")

    if numero < minimo:
        raise ValueError(f"{campo}: valor menor a {minimo}")

    if maximo is not None and numero > maximo:
        raise ValueError(f"{campo}: valor mayor a {maximo}")

    return numero


def validar_archivo(ruta):
    errores = []
    ids_registrados = {}
    total = 0

    try:
        with open(
            ruta, "r", encoding="utf-8-sig", newline=""
        ) as archivo:

            lector = csv.reader(archivo, strict=True)

            try:
                cabecera = next(lector)
            except StopIteration:
                return 0, ["El archivo CSV está vacío"]

            # Comprobar columnas y encabezados duplicados.
            if (
                len(cabecera) != len(COLUMNAS)
                or set(cabecera) != set(COLUMNAS)
            ):
                return 0, [
                    "Fila 1, estructura: columnas incorrectas. "
                    f"Esperadas: {COLUMNAS}. "
                    f"Encontradas: {cabecera}"
                ]

            for fila_numero, valores in enumerate(lector, start=2):
                total += 1

                if len(valores) != len(cabecera):
                    errores.append(
                        f"Fila {fila_numero}, estructura: "
                        f"se esperaban {len(cabecera)} campos, "
                        f"se encontraron {len(valores)}"
                    )
                    continue

                fila = dict(zip(cabecera, valores))

                # ID obligatorio, positivo y único.
                id_texto = fila["id"].strip()

                if not re.fullmatch(r"[0-9]+", id_texto):
                    errores.append(
                        f"Fila {fila_numero}, id: debe ser "
                        "un entero positivo"
                    )
                else:
                    identificador = int(id_texto)

                    if identificador <= 0:
                        errores.append(
                            f"Fila {fila_numero}, id: "
                            "debe ser mayor que cero"
                        )
                    elif identificador in ids_registrados:
                        errores.append(
                            f"Fila {fila_numero}, id: "
                            f"identificador duplicado "
                            f"(primera aparición en fila "
                            f"{ids_registrados[identificador]})"
                        )
                    else:
                        ids_registrados[identificador] = fila_numero

                # Textos obligatorios.
                for campo in ["name", "recclass"]:
                    if not fila[campo].strip():
                        errores.append(
                            f"Fila {fila_numero}, {campo}: "
                            "el texto es obligatorio"
                        )

                # Tipo de hallazgo.
                if fila["fall"].strip() not in ("Fell", "Found"):
                    errores.append(
                        f"Fila {fila_numero}, fall: "
                        "solo se acepta Fell o Found"
                    )

                # Masa.
                try:
                    validar_numero(
                        fila["mass (g)"], "mass (g)", 0
                    )
                except ValueError as error:
                    errores.append(f"Fila {fila_numero}, {error}")

                # Año.
                try:
                    obtener_anio(fila["year"])
                except ValueError as error:
                    errores.append(
                        f"Fila {fila_numero}, year: {error}"
                    )

                # Latitud y longitud.
                for campo, minimo, maximo in [
                    ("reclat", -90, 90),
                    ("reclong", -180, 180)
                ]:
                    try:
                        validar_numero(
                            fila[campo], campo, minimo, maximo
                        )
                    except ValueError as error:
                        errores.append(
                            f"Fila {fila_numero}, {error}"
                        )

    except (OSError, UnicodeError, csv.Error) as error:
        errores.append(f"Error de lectura del CSV: {error}")

    return total, errores


if __name__ == "__main__":
    proyecto = Path(__file__).resolve().parents[1]
    ruta_csv = proyecto / "datos" / "meteoritos.csv"

    total, errores = validar_archivo(ruta_csv)

    print("=" * 55)
    print("VALIDACIÓN DE DATOS DE METEORITOS")
    print("=" * 55)
    print(f"Registros analizados: {total}")
    print(f"Errores encontrados: {len(errores)}")

    if errores:
        print("\nVALIDACIÓN FALLIDA")

        for error in errores[:20]:
            print(f"ERROR: {error}")

        if len(errores) > 20:
            print(f"... y {len(errores) - 20} errores más")

        sys.exit(1)

    print("\nVALIDACIÓN EXITOSA")
    print("Todos los registros cumplen las reglas.")
    sys.exit(0)
