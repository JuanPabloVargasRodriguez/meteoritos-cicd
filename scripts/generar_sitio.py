
import os
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from scripts.analizar_datos import analizar_archivo


def formato(numero, decimales=0):
    """Formatea números al estilo español."""
    texto = f"{numero:,.{decimales}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def seguro(valor):
    """Evita que el contenido del CSV se interprete como HTML."""
    return escape(str(valor), quote=True)


def mostrar(valor):
    """Representa los datos opcionales faltantes."""
    valor = str(valor).strip()
    return seguro(valor) if valor else '<span class="missing">Sin dato</span>'


def tarjeta(titulo, valor, descripcion):
    return f"""
    <article class="kpi">
        <p>{seguro(titulo)}</p>
        <strong>{seguro(valor)}</strong>
        <small>{seguro(descripcion)}</small>
    </article>
    """


ESTILOS = """
:root {
    --fondo: #0b1020;
    --panel: #151d33;
    --borde: #2b3654;
    --texto: #f4f6ff;
    --muted: #a5b0ca;
    --cyan: #46d8ef;
    --purple: #a38bff;
    --green: #59dbb0;
}

* { box-sizing: border-box; }

body {
    margin: 0;
    background: var(--fondo);
    color: var(--texto);
    font-family: Inter, system-ui, Arial, sans-serif;
    line-height: 1.55;
}

.container {
    max-width: 1250px;
    margin: auto;
    padding: 28px 22px 70px;
}

header {
    padding: 34px 0 28px;
}

.eyebrow {
    color: var(--cyan);
    font-size: .8rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 2px;
}

h1 {
    margin: 10px 0;
    font-size: clamp(2rem, 5vw, 3.5rem);
    line-height: 1.12;
    letter-spacing: -1.5px;
}

h2 { font-size: 1.25rem; margin: 0 0 20px; }

.subtitle, .muted, small { color: var(--muted); }

.subtitle { max-width: 740px; }

.meta {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    margin-top: 22px;
}

.tag {
    padding: 7px 12px;
    background: #1c2943;
    border: 1px solid var(--borde);
    border-radius: 50px;
    font-size: .78rem;
    color: #d4e7ff;
}

.kpis {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 22px;
}

.kpi, .panel {
    background: var(--panel);
    border: 1px solid var(--borde);
    border-radius: 16px;
}

.kpi { padding: 22px; }

.kpi p {
    margin: 0 0 12px;
    font-size: .85rem;
    color: var(--muted);
}

.kpi strong {
    display: block;
    font-size: clamp(1.3rem, 2.3vw, 2rem);
    letter-spacing: -.7px;
}

.kpi small { font-size: .76rem; }

.panel {
    padding: 24px;
    margin-bottom: 22px;
    min-width: 0;
}

.charts {
    display: grid;
    grid-template-columns: 1.6fr 1fr;
    gap: 22px;
}

.bar-row {
    display: grid;
    grid-template-columns: minmax(80px, 140px) 1fr 65px;
    align-items: center;
    gap: 12px;
    margin-bottom: 13px;
    font-size: .84rem;
}

.bar-label {
    overflow-wrap: anywhere;
    color: #d9e4fb;
}

.bar-track {
    height: 13px;
    border-radius: 20px;
    background: #293550;
    overflow: hidden;
}

.bar-fill {
    display: block;
    height: 100%;
    border-radius: 20px;
    background: linear-gradient(90deg, var(--cyan), var(--purple));
}

.bar-value { text-align: right; color: var(--muted); }

.donut {
    width: min(220px, 80%);
    aspect-ratio: 1;
    margin: 15px auto 25px;
    border-radius: 50%;
    background: conic-gradient(
        var(--cyan) 0 var(--fell),
        var(--purple) var(--fell) 100%
    );
    display: grid;
    place-items: center;
}

.donut-center {
    width: 70%;
    aspect-ratio: 1;
    border-radius: 50%;
    background: var(--panel);
    display: grid;
    place-content: center;
    text-align: center;
}

.donut-center strong { font-size: 1.65rem; }
.donut-center small { font-size: .8rem; }

.legend {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 20px;
}

.dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 6px;
}

.cyan { background: var(--cyan); }
.purple { background: var(--purple); }

.table-wrap {
    width: 100%;
    overflow-x: auto;
}

table {
    border-collapse: collapse;
    width: 100%;
    font-size: .85rem;
    min-width: 690px;
}

th {
    background: #1e2944;
    text-align: left;
    color: #b9c8e7;
    font-weight: 600;
}

td, th {
    padding: 13px 12px;
    border-bottom: 1px solid var(--borde);
}

td { overflow-wrap: anywhere; }

tbody tr:hover { background: #202c47; }

.missing { color: #97a4c2; font-style: italic; }

.pill {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: .75rem;
}

.fell { background: #153f48; color: #77e8ed; }
.found { background: #392e59; color: #d8b9ff; }

.note {
    padding: 16px;
    border-left: 3px solid var(--cyan);
    background: #14243b;
    border-radius: 8px;
    font-size: .85rem;
    color: #cfdbef;
}

.search {
    background: #0e172a;
    color: white;
    border: 1px solid var(--borde);
    padding: 11px 13px;
    border-radius: 9px;
    width: 100%;
    max-width: 330px;
    margin: 0 0 16px;
}

footer {
    padding-top: 10px;
    color: var(--muted);
    font-size: .82rem;
    overflow-wrap: anywhere;
}

a { color: var(--cyan); }
code { overflow-wrap: anywhere; }

@media (max-width: 900px) {
    .kpis { grid-template-columns: repeat(2, 1fr); }
    .charts { grid-template-columns: 1fr; }
}

@media (max-width: 520px) {
    .container { padding: 15px 12px 45px; }
    .kpis { grid-template-columns: 1fr; }
    .kpi, .panel { padding: 17px; }
    .bar-row {
        grid-template-columns: 80px 1fr 48px;
        gap: 7px;
        font-size: .72rem;
    }
}
"""


JAVASCRIPT = """
const buscador = document.querySelector("#buscador");
const filas = document.querySelectorAll("#recientes tbody tr");
const contador = document.querySelector("#filas-visibles");

buscador.addEventListener("input", () => {
    const texto = buscador.value.toLowerCase().trim();
    let visibles = 0;

    filas.forEach(fila => {
        const coincide = fila.textContent.toLowerCase().includes(texto);
        fila.hidden = !coincide;
        if (coincide) visibles++;
    });

    contador.textContent = `${visibles} de ${filas.length} registros visibles`;
});
"""


def crear_html(indicadores, commit="LOCAL"):
    total = indicadores["total"]
    fell = indicadores["fell"]
    found = indicadores["found"]
    sin_masa = indicadores["sin_masa"]
    media = indicadores["masa_media"]

    porcentaje_fell = (fell / total * 100) if total else 0
    porcentaje_found = (found / total * 100) if total else 0
    porcentaje_faltante = (sin_masa / total * 100) if total else 0

    fecha = datetime.now(timezone.utc).strftime(
        "%d/%m/%Y %H:%M UTC"
    )

    # Tarjetas con los indicadores del CSV.
    tarjetas = "".join([
        tarjeta("Meteoritos registrados", formato(total), "Total de filas"),
        tarjeta("Fell", formato(fell),
                f"{porcentaje_fell:.2f}% de los registros"),
        tarjeta("Found", formato(found),
                f"{porcentaje_found:.2f}% de los registros"),
        tarjeta("Masa media", 
                formato(media, 2) + " g" if media is not None else "N/D",
                "Solo masas disponibles"),
        tarjeta("Sin información de masa", formato(sin_masa),
                f"{porcentaje_faltante:.2f}% de los registros")
    ])

    # Gráfico de las diez clases más frecuentes.
    clases = indicadores["top_clasificaciones"]
    maximo = max((cantidad for _, cantidad in clases), default=1)

    barras = ""
    for clase, cantidad in clases:
        ancho = cantidad / maximo * 100
        barras += f"""
        <div class="bar-row">
            <span class="bar-label">{seguro(clase)}</span>
            <div class="bar-track">
                <span class="bar-fill" style="width:{ancho:.2f}%"></span>
            </div>
            <span class="bar-value">{formato(cantidad)}</span>
        </div>
        """

    # Ranking de los meteoritos más pesados.
    ranking = ""
    for posicion, meteorito in enumerate(
        indicadores["ranking_masas"], start=1
    ):
        ranking += f"""
        <tr>
            <td>{posicion}</td>
            <td>{seguro(meteorito["name"])}</td>
            <td>{seguro(meteorito["id"])}</td>
            <td>{formato(meteorito["masa_g"], 2)}</td>
        </tr>
        """

    # Últimas diez filas, conservando el orden del CSV.
    recientes = ""
    for registro in indicadores["ultimos_registros"]:
        tipo = registro["fall"].strip()
        clase_tipo = "fell" if tipo == "Fell" else "found"

        recientes += f"""
        <tr>
            <td>{mostrar(registro["id"])}</td>
            <td>{mostrar(registro["name"])}</td>
            <td>{mostrar(registro["recclass"])}</td>
            <td>{mostrar(registro["mass (g)"])}</td>
            <td><span class="pill {clase_tipo}">{seguro(tipo)}</span></td>
            <td>{mostrar(registro["year"])}</td>
            <td>{mostrar(registro["reclat"])}</td>
            <td>{mostrar(registro["reclong"])}</td>
        </tr>
        """

    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description"
          content="Observatorio de meteoritos basado en datos abiertos de NASA">
    <title>Meteorite Observatory | CI/CD</title>
    <style>{ESTILOS}</style>
</head>
<body>
<div class="container">

<header>
    <div class="eyebrow">NASA Open Data · CI/CD Observatory</div>
    <h1>Meteorite Observatory</h1>
    <p class="subtitle">
        Exploración estadística de los meteoritos registrados en la Tierra.
        Dashboard generado automáticamente con Python y publicado mediante
        GitHub Actions.
    </p>
    <div class="meta">
        <span class="tag">Estudiante: Juan Pablo Vargas</span>
        <span class="tag">Ingeniería en Ciencia de Datos</span>
        <span class="tag">GitHub Actions + Python</span>
    </div>
</header>

<section class="kpis" aria-label="Indicadores principales">
    {tarjetas}
</section>

<section class="charts">
    <article class="panel">
        <h2>Top 10 clasificaciones</h2>
        <p class="muted">Número de registros por clase de meteorito.</p>
        <div role="img" aria-label="Gráfico de las diez clasificaciones más frecuentes">
            {barras}
        </div>
    </article>

    <article class="panel">
        <h2>Tipo de registro</h2>
        <p class="muted">Caídas observadas frente a hallazgos posteriores.</p>
        <div class="donut" style="--fell:{porcentaje_fell:.4f}%"
             role="img"
             aria-label="Fell {porcentaje_fell:.2f} por ciento; Found {porcentaje_found:.2f} por ciento">
            <div class="donut-center">
                <strong>{formato(total)}</strong>
                <small>meteoritos</small>
            </div>
        </div>
        <div class="legend">
            <span><i class="dot cyan"></i>Fell: {porcentaje_fell:.2f}%</span>
            <span><i class="dot purple"></i>Found: {porcentaje_found:.2f}%</span>
        </div>
    </article>
</section>

<section class="panel">
    <h2>Los 10 meteoritos de mayor masa</h2>
    <p class="muted">Ranking ordenado por masa registrada, en gramos.</p>
    <div class="table-wrap">
        <table>
            <thead>
                <tr><th>#</th><th>Meteorito</th><th>ID</th><th>Masa (g)</th></tr>
            </thead>
            <tbody>{ranking}</tbody>
        </table>
    </div>
</section>

<section class="panel" id="recientes">
    <h2>Últimos 10 registros del CSV</h2>
    <p class="muted">
        Permite comprobar las incorporaciones realizadas en el repositorio.
    </p>
    <input class="search" id="buscador" type="search"
           placeholder="Buscar en los últimos registros..."
           aria-label="Buscar registros recientes">
    <p id="filas-visibles" class="muted">10 de 10 registros visibles</p>
    <div class="table-wrap">
        <table>
            <thead>
                <tr>
                    <th>ID</th><th>Nombre</th><th>Clase</th>
                    <th>Masa (g)</th><th>Tipo</th><th>Año</th>
                    <th>Latitud</th><th>Longitud</th>
                </tr>
            </thead>
            <tbody>{recientes}</tbody>
        </table>
    </div>
</section>

<section class="panel">
    <h2>Fuente y metodología</h2>
    <p>
        Datos obtenidos del conjunto
        <a href="https://data.nasa.gov/dataset/meteorite-landings"
           target="_blank" rel="noopener noreferrer">
            Meteorite Landings — NASA Open Data
        </a>, con información de The Meteoritical Society.
        La muestra inicial conserva las primeras 20.000 filas.
    </p>
    <div class="note">
        <strong>Aviso académico:</strong>
        los meteoritos ficticios que se incorporen para demostrar el
        funcionamiento de CI/CD son simulaciones educativas y no
        representan nuevos hallazgos reales de la NASA.
    </div>
    <p class="muted">
        Los valores faltantes de masa no se convierten en cero y
        no intervienen en el cálculo de la media. Cada publicación
        exige superar las pruebas automatizadas y la validación completa.
    </p>
</section>

<footer>
    <p>Generado: {seguro(fecha)} · Commit: <code>{seguro(commit)}</code></p>
    <p>Proyecto académico · GitHub Actions · GitHub Pages</p>
</footer>

</div>
<script>{JAVASCRIPT}</script>
</body>
</html>
"""


def main():
    proyecto = Path(__file__).resolve().parents[1]
    archivo_csv = proyecto / "datos" / "meteoritos.csv"
    carpeta_publica = proyecto / "public"

    print("Analizando los datos...")
    indicadores = analizar_archivo(archivo_csv)

    commit = os.environ.get("GITHUB_SHA", "LOCAL")
    html = crear_html(indicadores, commit)

    carpeta_publica.mkdir(parents=True, exist_ok=True)
    destino = carpeta_publica / "index.html"
    destino.write_text(html, encoding="utf-8")

    print("SITIO GENERADO CORRECTAMENTE")
    print(f"Registros procesados: {indicadores['total']}")
    print(f"Archivo HTML: {destino}")
    print(f"Commit: {commit}")


if __name__ == "__main__":
    main()
