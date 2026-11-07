
import csv
from itertools import islice
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]

origen = BASE / "original" / "Meteorite_Landings.csv"
destino = BASE / "datos" / "meteoritos.csv"

columnas = [
    "id", "name", "recclass", "mass (g)",
    "fall", "year", "reclat", "reclong"
]

destino.parent.mkdir(exist_ok=True)

with origen.open("r", encoding="utf-8-sig", newline="") as archivo:
    lector = csv.DictReader(archivo)

    faltantes = set(columnas) - set(lector.fieldnames or [])
    if faltantes:
        raise ValueError(f"Faltan columnas: {faltantes}")

    registros = list(islice(lector, 20000))

    if len(registros) != 20000:
        raise ValueError(
            f"Se esperaban 20000 filas, hay {len(registros)}"
        )

    with destino.open("w", encoding="utf-8", newline="") as salida:
        escritor = csv.DictWriter(salida, fieldnames=columnas)
        escritor.writeheader()

        for registro in registros:
            escritor.writerow({
                columna: registro[columna] for columna in columnas
            })

print("Muestra generada correctamente")
print(f"Registros: {len(registros):,}")
print(f"Columnas: {len(columnas)}")
print(f"Archivo: {destino}")
