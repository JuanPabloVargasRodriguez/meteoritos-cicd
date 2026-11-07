
import csv
from collections import Counter
from pathlib import Path

from scripts.validar_datos import validar_archivo


def calcular_indicadores(registros):
    registros = list(registros)

    masas = []
    for fila in registros:
        valor = fila["mass (g)"].strip()
        if valor:
            masas.append((fila, float(valor)))

    clases = Counter(
        fila["recclass"].strip()
        for fila in registros
    )

    ranking = sorted(
        [
            {
                "id": fila["id"],
                "name": fila["name"],
                "masa_g": masa
            }
            for fila, masa in masas
        ],
        key=lambda item: item["masa_g"],
        reverse=True
    )[:10]

    return {
        "total": len(registros),
        "fell": sum(
            fila["fall"].strip() == "Fell"
            for fila in registros
        ),
        "found": sum(
            fila["fall"].strip() == "Found"
            for fila in registros
        ),
        "masa_media": (
            sum(masa for _, masa in masas) / len(masas)
            if masas else None
        ),
        "sin_masa": len(registros) - len(masas),
        "top_clasificaciones": clases.most_common(10),
        "ranking_masas": ranking,
        "ultimos_registros": registros[-10:]
    }


def analizar_archivo(ruta):
    total, errores = validar_archivo(ruta)

    if errores:
        raise ValueError(
            "El CSV contiene datos inválidos:\n"
            + "\n".join(errores[:20])
        )

    with open(ruta, encoding="utf-8-sig", newline="") as archivo:
        registros = list(csv.DictReader(archivo))

    return calcular_indicadores(registros)


if __name__ == "__main__":
    base = Path(__file__).resolve().parents[1]
    ruta = base / "datos" / "meteoritos.csv"

    resultado = analizar_archivo(ruta)

    print("\n=== INDICADORES DE METEORITOS ===")
    print("Total:", resultado["total"])
    print("Fell:", resultado["fell"])
    print("Found:", resultado["found"])
    print("Sin masa:", resultado["sin_masa"])

    media = resultado["masa_media"]
    print(
        "Masa media:",
        f"{media:,.2f} g" if media is not None else "Sin datos"
    )
