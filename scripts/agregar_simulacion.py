
import argparse
import csv
from pathlib import Path

RUTA = Path(__file__).resolve().parents[1] / "datos" / "meteoritos.csv"

COLUMNAS = [
    "id", "name", "recclass", "mass (g)",
    "fall", "year", "reclat", "reclong"
]

CASOS = {
    "valido": {
        "name": "SIMULADO-Prueba-clase",
        "mass (g)": "1234.5",
        "reclat": "12.345",
        "reclong": "-45.678",
    },
    "masa-negativa": {
        "name": "SIMULADO-ERROR-MASA",
        "mass (g)": "-500",
        "reclat": "12.345",
        "reclong": "-45.678",
    },
    "coordenada-invalida": {
        "name": "SIMULADO-ERROR-COORDENADA",
        "mass (g)": "750",
        "reclat": "120",
        "reclong": "-45.678",
    },
    "id-duplicado": {
        "name": "SIMULADO-ERROR-DUPLICADO",
        "mass (g)": "750",
        "reclat": "12.345",
        "reclong": "-45.678",
    }
}


def agregar_simulacion(caso):
    with RUTA.open("r", encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        encabezados = lector.fieldnames

        if not encabezados or set(encabezados) != set(COLUMNAS):
            raise ValueError("El CSV no tiene las columnas esperadas")

        registros = list(lector)

    nombre = CASOS[caso]["name"]

    if any(fila["name"] == nombre for fila in registros):
        raise ValueError("Esta simulación ya existe en el CSV")

    ids = [int(fila["id"]) for fila in registros]
    nuevo_id = max(ids, default=0) + 1

    if caso == "id-duplicado":
        nuevo_id = ids[0]

    registro = {
        "id": str(nuevo_id),
        "name": nombre,
        "recclass": "L6",
        "mass (g)": "1234.5",
        "fall": "Found",
        "year": "2026",
        "reclat": "12.345",
        "reclong": "-45.678",
    }

    registro.update(CASOS[caso])

    # Comprobar que el archivo termina en salto de línea.
    with RUTA.open("rb") as archivo:
        archivo.seek(0, 2)
        tamano = archivo.tell()
        archivo.seek(-1, 2) if tamano else None
        ultimo = archivo.read(1) if tamano else b"\n"

    with RUTA.open("a", encoding="utf-8", newline="") as archivo:
        if ultimo not in (b"\n", b"\r"):
            archivo.write("\n")

        escritor = csv.DictWriter(
            archivo, fieldnames=encabezados
        )
        escritor.writerow(registro)

    print("=" * 50)
    print(f"Simulación: {caso}")
    print(f"ID: {registro['id']}")
    print(f"Nombre: {nombre}")
    print(f"Registros esperados: {len(registros) + 1}")
    print("Registro añadido al final del CSV")
    print("=" * 50)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "caso",
        choices=list(CASOS)
    )
    argumentos = parser.parse_args()
    agregar_simulacion(argumentos.caso)
