import json
import os
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from scripts.analizar_datos import analizar_archivo


def formato(numero, decimales=0):
    """Formatea números al estilo español (puntos para miles, coma para decimales)."""
    if numero is None:
        return "N/D"
    texto = f"{numero:,.{decimales}f}"
    return texto.replace(",", "_").replace(".", ",").replace("_", ".")


def formato_metricas_masa(gramos):
    """Calcula equivalencias útiles en kilogramos y toneladas métricas."""
    if gramos is None:
        return "N/D", "N/D"
    kg = gramos / 1000.0
    ton = gramos / 1000000.0
    return formato(kg, 2) + " kg", formato(ton, 2) + " t"


def seguro(valor):
    """Evita que el contenido del CSV se interprete como HTML."""
    if valor is None:
        return ""
    return escape(str(valor), quote=True)


def mostrar(valor):
    """Representa los datos opcionales faltantes con indicador semántico."""
    if valor is None:
        return '<span class="missing">Sin dato</span>'
    texto = str(valor).strip()
    return seguro(texto) if texto else '<span class="missing">Sin dato</span>'


def serializar_registro(registro):
    """Serializa un registro del CSV de forma segura para atributos data-*."""
    payload = {
        "id": str(registro.get("id", "")).strip(),
        "name": str(registro.get("name", "")).strip(),
        "recclass": str(registro.get("recclass", "")).strip(),
        "mass": str(registro.get("mass (g)", "")).strip(),
        "fall": str(registro.get("fall", "")).strip(),
        "year": str(registro.get("year", "")).strip(),
        "reclat": str(registro.get("reclat", "")).strip(),
        "reclong": str(registro.get("reclong", "")).strip(),
    }
    return escape(json.dumps(payload), quote=True)


def tarjeta_kpi(identificador, titulo, valor_formateado, valor_crudo, unidad, subtitulo, indicador, unidad_desc, metodo, codigo_obs="OBS-01"):
    """Genera una tarjeta KPI con estética de instrumentación de observatorio espacial."""
    raw_attr = f'data-target="{valor_crudo}"' if valor_crudo is not None else ""
    return f"""
    <article class="kpi-card" id="kpi-{seguro(identificador)}" tabindex="0">
        <span class="corner-bracket corner-tl" aria-hidden="true"></span>
        <span class="corner-bracket corner-tr" aria-hidden="true"></span>
        <span class="corner-bracket corner-bl" aria-hidden="true"></span>
        <span class="corner-bracket corner-br" aria-hidden="true"></span>

        <div class="kpi-header">
            <div class="kpi-tag-group">
                <span class="kpi-obs-code">{seguro(codigo_obs)}</span>
                <span class="kpi-badge">{seguro(unidad)}</span>
            </div>
            <div class="kpi-tooltip-box">
                <button type="button" class="kpi-info-btn" aria-label="Información metodológica sobre {seguro(titulo)}" aria-expanded="false">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="16" x2="12" y2="12"></line>
                        <line x1="12" y1="8" x2="12.01" y2="8"></line>
                    </svg>
                </button>
                <div class="kpi-tooltip" role="tooltip">
                    <div class="tooltip-title">{seguro(titulo)}</div>
                    <div class="tooltip-row"><span class="tooltip-label">Indicador:</span> {seguro(indicador)}</div>
                    <div class="tooltip-row"><span class="tooltip-label">Unidad:</span> {seguro(unidad_desc)}</div>
                    <div class="tooltip-row"><span class="tooltip-label">Método:</span> {seguro(metodo)}</div>
                </div>
            </div>
        </div>
        <p class="kpi-label">{seguro(titulo)}</p>
        <div class="kpi-value-wrap">
            <strong class="kpi-value" {raw_attr}>{seguro(valor_formateado)}</strong>
        </div>
        <div class="kpi-footer-row">
            <small class="kpi-sub">{seguro(subtitulo)}</small>
            <div class="kpi-spectrum" aria-hidden="true">
                <span class="bar-s1"></span><span class="bar-s2"></span><span class="bar-s3"></span><span class="bar-s4"></span>
            </div>
        </div>
        <div class="kpi-border-beam" aria-hidden="true"></div>
    </article>
    """


ESTILOS = """
:root {
    --space-void: #03060f;
    --space-deep: #070c18;
    --space-surface: #0c1426;
    --space-surface-hover: #121d36;
    --space-surface-active: #19284a;
    --space-border: #1a2947;
    --space-border-light: #283e68;
    --space-border-glow: rgba(0, 229, 255, 0.4);

    --cyan: #00e5ff;
    --cyan-dim: rgba(0, 229, 255, 0.15);
    --cyan-glow: 0 0 24px rgba(0, 229, 255, 0.5);
    --purple: #a855f7;
    --purple-dim: rgba(168, 85, 247, 0.15);
    --purple-glow: 0 0 24px rgba(168, 85, 247, 0.5);
    --blue: #38bdf8;
    --blue-glow: 0 0 20px rgba(56, 189, 248, 0.4);
    --green: #10b981;
    --green-glow: 0 0 16px rgba(16, 185, 129, 0.5);
    --amber: #f59e0b;
    --amber-glow: 0 0 20px rgba(245, 158, 11, 0.4);

    --text-pure: #f8fafc;
    --text-soft: #cbd5e1;
    --text-muted: #8294b2;
    --text-dim: #4d5e7a;

    --font-sans: 'Plus Jakarta Sans', system-ui, -apple-system, 'Segoe UI', Roboto, sans-serif;
    --font-mono: 'JetBrains Mono', 'SF Mono', Consolas, 'Courier New', monospace;

    --radius-sm: 8px;
    --radius-md: 14px;
    --radius-lg: 20px;
    --radius-pill: 9999px;

    --transition-fast: 0.18s cubic-bezier(0.16, 1, 0.3, 1);
    --transition-smooth: 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}

*, *::before, *::after {
    box-sizing: border-box;
}

html {
    color-scheme: dark;
    scroll-behavior: smooth;
}

body {
    margin: 0;
    background-color: var(--space-void);
    color: var(--text-pure);
    font-family: var(--font-sans);
    line-height: 1.6;
    overflow-x: hidden;
    position: relative;
    min-height: 100vh;
    font-feature-settings: 'cv02', 'cv03', 'cv04', 'cv11';
}

/* Lienzo de cielo profundo, estrellas multicapa, nebulosa y meteoros */
#space-canvas {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: -1;
    pointer-events: none;
}

/* Enfoque accesible */
:focus-visible {
    outline: 2px solid var(--cyan);
    outline-offset: 3px;
    box-shadow: var(--cyan-glow);
}

/* Contenedor principal con retícula */
.container {
    max-width: 1300px;
    margin: 0 auto;
    padding: 24px 24px 90px;
    position: relative;
    z-index: 1;
}

/* Esquinas de retícula / Instrumento de Observatorio */
.corner-bracket {
    position: absolute;
    width: 10px;
    height: 10px;
    border-color: var(--cyan);
    pointer-events: none;
    opacity: 0.6;
    transition: var(--transition-fast);
}

.kpi-card:hover .corner-bracket,
.panel:hover .corner-bracket {
    opacity: 1;
    border-color: var(--cyan);
    box-shadow: 0 0 8px var(--cyan);
}

.corner-tl { top: -1px; left: -1px; border-top: 2px solid var(--cyan); border-left: 2px solid var(--cyan); }
.corner-tr { top: -1px; right: -1px; border-top: 2px solid var(--cyan); border-right: 2px solid var(--cyan); }
.corner-bl { bottom: -1px; left: -1px; border-bottom: 2px solid var(--cyan); border-left: 2px solid var(--cyan); }
.corner-br { bottom: -1px; right: -1px; border-bottom: 2px solid var(--cyan); border-right: 2px solid var(--cyan); }

/* Barra superior de telemetría y estado */
.telemetry-bar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
    padding: 12px 20px;
    background: rgba(12, 20, 38, 0.75);
    backdrop-filter: blur(14px);
    border: 1px solid var(--space-border);
    border-radius: var(--radius-md);
    margin-bottom: 28px;
    font-size: 0.82rem;
    font-family: var(--font-mono);
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.4);
}

.telemetry-status {
    display: flex;
    align-items: center;
    gap: 12px;
    color: var(--green);
    letter-spacing: 0.5px;
}

.beacon-pulse-group {
    position: relative;
    width: 14px;
    height: 14px;
    display: grid;
    place-items: center;
}

.beacon-core {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background-color: var(--green);
    box-shadow: 0 0 10px var(--green);
}

.beacon-pulse {
    position: absolute;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    border: 1.5px solid var(--green);
    animation: radarPulse 2s infinite ease-out;
}

@keyframes radarPulse {
    0% { transform: scale(0.6); opacity: 1; }
    70% { transform: scale(1.6); opacity: 0; }
    100% { transform: scale(0.6); opacity: 0; }
}

/* Onda de señal osciloscópica en tiempo real */
.telemetry-wave-wrap {
    display: flex;
    align-items: center;
    gap: 10px;
    color: var(--cyan);
}

.telemetry-waveform {
    width: 110px;
    height: 18px;
    overflow: hidden;
}

.wave-path {
    stroke: var(--cyan);
    stroke-width: 1.6;
    stroke-dasharray: 200;
    stroke-dashoffset: 0;
    animation: waveStream 3.5s linear infinite;
    filter: drop-shadow(0 0 4px var(--cyan));
}

@keyframes waveStream {
    from { stroke-dashoffset: 400; }
    to { stroke-dashoffset: 0; }
}

.telemetry-meta {
    display: flex;
    align-items: center;
    gap: 16px;
    color: var(--text-muted);
    flex-wrap: wrap;
}

.telemetry-item {
    display: flex;
    align-items: center;
    gap: 6px;
}

.telemetry-item code {
    background: rgba(0, 229, 255, 0.1);
    color: var(--cyan);
    padding: 2px 8px;
    border-radius: var(--radius-sm);
    border: 1px solid rgba(0, 229, 255, 0.25);
    font-size: 0.8rem;
}

/* Rastreador de coordenadas astronómicas del telescopio */
.telescope-coords {
    color: var(--amber);
    background: rgba(245, 158, 11, 0.08);
    border: 1px solid rgba(245, 158, 11, 0.25);
    padding: 3px 9px;
    border-radius: var(--radius-sm);
    font-size: 0.76rem;
}

/* Encabezado / Hero del Observatorio */
.hero-observatory {
    display: grid;
    grid-template-columns: 1.35fr 0.85fr;
    align-items: center;
    gap: 32px;
    padding: 38px 40px;
    background: linear-gradient(135deg, rgba(12, 20, 38, 0.9) 0%, rgba(7, 12, 24, 0.95) 100%);
    border: 1px solid var(--space-border);
    border-radius: var(--radius-lg);
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.08);
}

.hero-observatory::before {
    content: "";
    position: absolute;
    top: -140px;
    right: -140px;
    width: 440px;
    height: 440px;
    background: radial-gradient(circle, rgba(0, 229, 255, 0.22) 0%, rgba(168, 85, 247, 0.1) 45%, transparent 75%);
    pointer-events: none;
    animation: nebulaDrift 16s ease-in-out infinite alternate;
}

@keyframes nebulaDrift {
    0% { transform: scale(1) translate(0, 0); opacity: 0.8; }
    100% { transform: scale(1.15) translate(-20px, 15px); opacity: 1; }
}

.hero-content {
    position: relative;
    z-index: 2;
}

.eyebrow {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-family: var(--font-mono);
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 2px;
    color: var(--cyan);
    margin-bottom: 12px;
}

.eyebrow-dot {
    width: 7px;
    height: 7px;
    border-radius: 50%;
    background: var(--cyan);
    box-shadow: 0 0 10px var(--cyan);
    animation: blinkLight 1.8s infinite;
}

@keyframes blinkLight {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}

h1 {
    margin: 0 0 14px;
    font-size: clamp(2.3rem, 4.4vw, 3.6rem);
    font-weight: 800;
    line-height: 1.12;
    letter-spacing: -1.8px;
    background: linear-gradient(180deg, #ffffff 30%, #b5cde8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.subtitle {
    margin: 0 0 24px;
    font-size: 1.05rem;
    color: var(--text-soft);
    max-width: 660px;
    line-height: 1.6;
}

.hero-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.hero-tag {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    padding: 7px 14px;
    background: rgba(18, 29, 54, 0.7);
    border: 1px solid var(--space-border-light);
    border-radius: var(--radius-pill);
    font-size: 0.8rem;
    color: #e2e8f0;
    transition: var(--transition-fast);
}

.hero-tag:hover {
    border-color: var(--cyan);
    background: rgba(0, 229, 255, 0.12);
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 229, 255, 0.2);
}

.hero-tag svg {
    color: var(--cyan);
}

/* Escáner de Radar Interactivo de Espacio Profundo (Hero Instrument) */
.hero-art {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    position: relative;
    user-select: none;
}

.radar-console {
    position: relative;
    width: 100%;
    max-width: 320px;
    aspect-ratio: 1;
    display: grid;
    place-items: center;
}

.radar-art-svg {
    width: 100%;
    height: 100%;
    filter: drop-shadow(0 0 28px rgba(0, 229, 255, 0.28));
}

.radar-sweep-cone {
    transform-origin: 150px 150px;
    animation: radarScan 7s linear infinite;
}

@keyframes radarScan {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.radar-orbit {
    transform-origin: 150px 150px;
    animation: rotateOrbit 36s linear infinite;
}

@keyframes rotateOrbit {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.radar-blip {
    animation: blipGlow 3.5s ease-in-out infinite;
}

.blip-1 { animation-delay: 0.5s; }
.blip-2 { animation-delay: 1.8s; }
.blip-3 { animation-delay: 2.7s; }

@keyframes blipGlow {
    0%, 100% { opacity: 0.3; transform: scale(0.9); }
    50% { opacity: 1; transform: scale(1.3); filter: drop-shadow(0 0 8px var(--cyan)); }
}

/* Selector interactivo de modo del escáner */
.scanner-controls {
    display: flex;
    gap: 8px;
    margin-top: 14px;
}

.scan-mode-btn {
    background: rgba(14, 23, 44, 0.8);
    border: 1px solid var(--space-border-light);
    color: var(--text-muted);
    font-family: var(--font-mono);
    font-size: 0.72rem;
    padding: 4px 10px;
    border-radius: var(--radius-sm);
    cursor: pointer;
    transition: var(--transition-fast);
}

.scan-mode-btn:hover, .scan-mode-btn.active {
    color: var(--cyan);
    border-color: var(--cyan);
    background: rgba(0, 229, 255, 0.12);
    box-shadow: 0 0 10px rgba(0, 229, 255, 0.25);
}

/* Grilla de Tarjetas KPI */
.kpis {
    display: grid;
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: 16px;
    margin-bottom: 34px;
}

.kpi-card {
    background: var(--space-surface);
    border: 1px solid var(--space-border);
    border-radius: var(--radius-md);
    padding: 22px 20px;
    position: relative;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    transition: var(--transition-smooth);
    cursor: default;
    overflow: hidden;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.3);
}

.kpi-card:hover {
    transform: translateY(-5px);
    border-color: var(--cyan);
    box-shadow: 0 14px 32px rgba(0, 0, 0, 0.5), 0 0 24px rgba(0, 229, 255, 0.2);
}

.kpi-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.kpi-tag-group {
    display: flex;
    align-items: center;
    gap: 8px;
}

.kpi-obs-code {
    font-family: var(--font-mono);
    font-size: 0.68rem;
    color: var(--text-dim);
    letter-spacing: 0.5px;
}

.kpi-badge {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    padding: 2px 7px;
    border-radius: var(--radius-sm);
    background: rgba(56, 189, 248, 0.12);
    color: var(--blue);
    border: 1px solid rgba(56, 189, 248, 0.25);
    letter-spacing: 0.5px;
}

.kpi-tooltip-box {
    position: relative;
}

.kpi-info-btn {
    background: transparent;
    border: 1px solid var(--space-border-light);
    color: var(--text-muted);
    border-radius: 50%;
    width: 24px;
    height: 24px;
    display: grid;
    place-items: center;
    cursor: pointer;
    transition: var(--transition-fast);
    padding: 0;
}

.kpi-info-btn:hover, .kpi-info-btn:focus-visible {
    color: var(--cyan);
    border-color: var(--cyan);
    background: rgba(0, 229, 255, 0.12);
}

.kpi-tooltip {
    position: absolute;
    bottom: calc(100% + 10px);
    right: 0;
    width: 250px;
    background: #0d1527;
    border: 1px solid var(--cyan);
    border-radius: var(--radius-sm);
    padding: 12px 14px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.8), var(--cyan-glow);
    font-size: 0.78rem;
    line-height: 1.45;
    color: var(--text-soft);
    pointer-events: none;
    opacity: 0;
    visibility: hidden;
    transform: translateY(6px);
    transition: var(--transition-fast);
    z-index: 100;
}

.kpi-info-btn:hover + .kpi-tooltip,
.kpi-info-btn:focus + .kpi-tooltip,
.kpi-tooltip-box:hover .kpi-tooltip,
.kpi-info-btn[aria-expanded="true"] + .kpi-tooltip {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

.tooltip-title {
    font-weight: 700;
    color: var(--cyan);
    margin-bottom: 6px;
    font-size: 0.82rem;
    border-bottom: 1px solid var(--space-border);
    padding-bottom: 4px;
}

.tooltip-row {
    margin-bottom: 4px;
}

.tooltip-label {
    color: var(--text-pure);
    font-weight: 600;
}

.kpi-label {
    margin: 0 0 8px;
    font-size: 0.86rem;
    color: var(--text-muted);
    font-weight: 500;
}

.kpi-value-wrap {
    margin-bottom: 8px;
}

.kpi-value {
    display: block;
    font-size: clamp(1.6rem, 2.2vw, 2.3rem);
    font-weight: 800;
    letter-spacing: -1px;
    color: var(--text-pure);
    font-variant-numeric: tabular-nums;
    font-family: var(--font-sans);
}

.kpi-footer-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
}

.kpi-sub {
    font-size: 0.77rem;
    color: var(--text-muted);
    line-height: 1.4;
}

/* Indicador de espectro/actividad en la tarjeta KPI */
.kpi-spectrum {
    display: flex;
    align-items: flex-end;
    gap: 3px;
    height: 14px;
}

.kpi-spectrum span {
    width: 2.5px;
    background: var(--cyan);
    border-radius: 1px;
    opacity: 0.6;
    animation: spectrumBounce 1.4s ease-in-out infinite alternate;
}

.kpi-spectrum .bar-s1 { height: 40%; animation-delay: 0.1s; }
.kpi-spectrum .bar-s2 { height: 80%; animation-delay: 0.4s; }
.kpi-spectrum .bar-s3 { height: 50%; animation-delay: 0.2s; }
.kpi-spectrum .bar-s4 { height: 95%; animation-delay: 0.6s; }

@keyframes spectrumBounce {
    0% { height: 25%; opacity: 0.4; }
    100% { height: 100%; opacity: 0.9; }
}

/* Paneles de Observación */
.panel {
    background: var(--space-surface);
    border: 1px solid var(--space-border);
    border-radius: var(--radius-lg);
    padding: 28px;
    margin-bottom: 34px;
    position: relative;
    box-shadow: 0 10px 36px rgba(0, 0, 0, 0.4);
}

.panel-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 22px;
    flex-wrap: wrap;
    gap: 12px;
    border-bottom: 1px solid var(--space-border);
    padding-bottom: 16px;
}

.panel-title-area h2 {
    margin: 0 0 6px;
    font-size: 1.35rem;
    font-weight: 700;
    letter-spacing: -0.5px;
    display: flex;
    align-items: center;
    gap: 10px;
}

.panel-icon-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--cyan);
    box-shadow: 0 0 8px var(--cyan);
}

.panel-desc {
    margin: 0;
    font-size: 0.88rem;
    color: var(--text-muted);
}

/* Grillas de Gráficos (Clases + Donut) */
.charts-grid {
    display: grid;
    grid-template-columns: 1.45fr 1fr;
    gap: 24px;
    margin-bottom: 34px;
}

/* Gráfico de barras de Clasificaciones con interacción y rayo láser */
.bar-chart-container {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.bar-row {
    display: grid;
    grid-template-columns: minmax(75px, 110px) 1fr 65px;
    align-items: center;
    gap: 12px;
    padding: 9px 14px;
    border-radius: var(--radius-sm);
    background: rgba(9, 15, 28, 0.5);
    border: 1px solid transparent;
    transition: var(--transition-fast);
    cursor: pointer;
    position: relative;
    overflow: hidden;
}

.bar-row:hover, .bar-row:focus-visible, .bar-row.active {
    background: rgba(0, 229, 255, 0.08);
    border-color: rgba(0, 229, 255, 0.35);
    transform: translateX(4px);
    box-shadow: inset 2px 0 0 var(--cyan);
}

.bar-label {
    font-family: var(--font-mono);
    font-size: 0.86rem;
    font-weight: 600;
    color: var(--cyan);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.bar-track {
    height: 12px;
    background: rgba(26, 41, 71, 0.7);
    border-radius: var(--radius-pill);
    overflow: hidden;
    position: relative;
}

.bar-fill {
    display: block;
    height: 100%;
    background: linear-gradient(90deg, var(--cyan) 0%, var(--purple) 100%);
    border-radius: var(--radius-pill);
    transition: width 0.8s cubic-bezier(0.16, 1, 0.3, 1);
    box-shadow: 0 0 12px rgba(0, 229, 255, 0.35);
    position: relative;
}

.bar-fill::after {
    content: "";
    position: absolute;
    right: 0;
    top: 0;
    bottom: 0;
    width: 6px;
    background: #ffffff;
    box-shadow: 0 0 8px #ffffff, 0 0 16px var(--cyan);
    border-radius: 50%;
}

.bar-value {
    text-align: right;
    font-family: var(--font-mono);
    font-size: 0.84rem;
    color: var(--text-soft);
    font-variant-numeric: tabular-nums;
}

/* HUD interactivo del gráfico de barras */
.chart-inspector-hud {
    margin-top: 14px;
    padding: 12px 18px;
    background: rgba(7, 12, 24, 0.85);
    border: 1px dashed var(--space-border-light);
    border-radius: var(--radius-sm);
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 0.83rem;
    color: var(--text-soft);
}

.hud-highlight {
    color: var(--cyan);
    font-weight: 700;
    font-family: var(--font-mono);
}

/* Gráfico circular Donut Fell / Found con satélite orbital */
.donut-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
}

.donut-graphic-wrapper {
    position: relative;
    width: 230px;
    height: 230px;
    margin: 10px auto 20px;
}

.donut-ring {
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background: conic-gradient(
        var(--cyan) 0 var(--fell-deg),
        var(--purple) var(--fell-deg) 360deg
    );
    display: grid;
    place-items: center;
    box-shadow: 0 0 32px rgba(0, 229, 255, 0.18);
    transition: transform var(--transition-fast);
    position: relative;
}

.donut-ring:hover {
    transform: scale(1.03);
}

/* Partícula satélite en órbita alrededor del Donut */
.donut-satellite-orbit {
    position: absolute;
    top: -10px;
    left: -10px;
    right: -10px;
    bottom: -10px;
    border-radius: 50%;
    border: 1px dashed rgba(0, 229, 255, 0.25);
    pointer-events: none;
    animation: orbitRotate 12s linear infinite;
}

.donut-satellite-dot {
    position: absolute;
    top: 0;
    left: 50%;
    width: 8px;
    height: 8px;
    margin-left: -4px;
    margin-top: -4px;
    border-radius: 50%;
    background: var(--cyan);
    box-shadow: 0 0 10px var(--cyan), 0 0 20px var(--cyan);
}

@keyframes orbitRotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

.donut-core {
    width: 72%;
    height: 72%;
    border-radius: 50%;
    background: var(--space-surface);
    border: 1px solid var(--space-border);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    box-shadow: inset 0 0 18px rgba(0, 0, 0, 0.7);
}

.donut-core strong {
    font-size: 1.65rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    font-family: var(--font-mono);
    color: var(--text-pure);
}

.donut-core small {
    font-size: 0.76rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 1px;
}

/* Tarjetas interactivas de Fell y Found */
.donut-segments-interactive {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    width: 100%;
    margin-top: 8px;
}

.segment-card {
    padding: 13px;
    border-radius: var(--radius-sm);
    background: rgba(9, 15, 28, 0.6);
    border: 1px solid var(--space-border);
    cursor: pointer;
    transition: var(--transition-fast);
    text-align: left;
}

.segment-card:hover, .segment-card:focus-visible, .segment-card.active {
    transform: translateY(-2px);
    background: rgba(20, 32, 58, 0.7);
}

.segment-card.fell-card:hover, .segment-card.fell-card.active {
    border-color: var(--cyan);
    box-shadow: 0 0 20px rgba(0, 229, 255, 0.25);
}

.segment-card.found-card:hover, .segment-card.found-card.active {
    border-color: var(--purple);
    box-shadow: 0 0 20px rgba(168, 85, 247, 0.25);
}

.segment-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 0.85rem;
    font-weight: 700;
    margin-bottom: 4px;
}

.segment-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
}

.dot-cyan { background: var(--cyan); box-shadow: 0 0 8px var(--cyan); }
.dot-purple { background: var(--purple); box-shadow: 0 0 8px var(--purple); }

.segment-stat {
    font-family: var(--font-mono);
    font-size: 0.82rem;
    color: var(--text-soft);
    margin-bottom: 4px;
}

.segment-desc {
    font-size: 0.74rem;
    color: var(--text-muted);
    line-height: 1.35;
}

/* Sección de Ranking de Masas con Inspector Dinámico */
.ranking-layout {
    display: grid;
    grid-template-columns: 1.3fr 0.9fr;
    gap: 24px;
    align-items: start;
}

.table-wrap {
    width: 100%;
    overflow-x: auto;
    border-radius: var(--radius-sm);
    border: 1px solid var(--space-border);
    background: rgba(7, 12, 24, 0.7);
}

table {
    border-collapse: collapse;
    width: 100%;
    font-size: 0.86rem;
    min-width: 600px;
}

th {
    background: rgba(14, 23, 44, 0.95);
    color: var(--text-muted);
    font-weight: 600;
    font-family: var(--font-mono);
    font-size: 0.78rem;
    text-transform: uppercase;
    letter-spacing: 0.7px;
    padding: 14px 16px;
    border-bottom: 1px solid var(--space-border);
    text-align: left;
}

td {
    padding: 13px 16px;
    border-bottom: 1px solid rgba(26, 41, 71, 0.6);
    color: var(--text-soft);
    transition: background var(--transition-fast);
}

tbody tr {
    cursor: pointer;
    transition: var(--transition-fast);
}

tbody tr:hover {
    background: rgba(0, 229, 255, 0.08) !important;
}

tbody tr.selected-row {
    background: rgba(0, 229, 255, 0.14) !important;
    border-left: 3px solid var(--cyan);
}

.rank-badge {
    display: inline-grid;
    place-items: center;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: rgba(56, 189, 248, 0.15);
    color: var(--blue);
    font-family: var(--font-mono);
    font-size: 0.78rem;
    font-weight: 700;
    border: 1px solid rgba(56, 189, 248, 0.3);
}

.rank-top-1 {
    background: rgba(245, 158, 11, 0.2);
    color: var(--amber);
    border-color: var(--amber);
    box-shadow: 0 0 12px rgba(245, 158, 11, 0.35);
}

/* Ficha / Spotlight de Masa lateral */
.mass-spotlight {
    background: linear-gradient(145deg, rgba(16, 26, 48, 0.92) 0%, rgba(7, 12, 24, 0.96) 100%);
    border: 1px solid var(--space-border-light);
    border-radius: var(--radius-md);
    padding: 26px;
    box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.06), 0 12px 32px rgba(0, 0, 0, 0.4);
    position: sticky;
    top: 24px;
}

.spotlight-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 18px;
    border-bottom: 1px solid var(--space-border);
    padding-bottom: 12px;
}

.spotlight-eyebrow {
    font-family: var(--font-mono);
    font-size: 0.74rem;
    color: var(--cyan);
    text-transform: uppercase;
    letter-spacing: 1.5px;
}

.spotlight-rank {
    font-family: var(--font-mono);
    font-size: 0.9rem;
    font-weight: 700;
    color: var(--amber);
}

.spotlight-name {
    margin: 0 0 8px;
    font-size: 1.55rem;
    font-weight: 800;
    color: var(--text-pure);
    letter-spacing: -0.5px;
}

.spotlight-id {
    font-family: var(--font-mono);
    font-size: 0.8rem;
    color: var(--text-muted);
    margin-bottom: 18px;
}

.mass-grid {
    display: grid;
    grid-template-columns: 1fr;
    gap: 10px;
    margin-bottom: 18px;
}

.mass-tile {
    background: rgba(9, 15, 28, 0.75);
    border: 1px solid var(--space-border);
    border-radius: var(--radius-sm);
    padding: 10px 14px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    transition: var(--transition-fast);
}

.mass-tile:hover {
    border-color: var(--cyan);
    background: rgba(0, 229, 255, 0.05);
}

.mass-tile-unit {
    font-size: 0.76rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.mass-tile-val {
    font-family: var(--font-mono);
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--cyan);
}

.spotlight-scale-wrap {
    margin-top: 14px;
}

.spotlight-scale-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.76rem;
    color: var(--text-muted);
    margin-bottom: 6px;
}

.spotlight-scale-track {
    height: 9px;
    background: rgba(26, 41, 71, 0.85);
    border-radius: var(--radius-pill);
    overflow: hidden;
}

.spotlight-scale-fill {
    height: 100%;
    background: linear-gradient(90deg, var(--cyan), var(--amber));
    border-radius: var(--radius-pill);
    transition: width 0.4s ease;
    box-shadow: 0 0 10px rgba(0, 229, 255, 0.4);
}

/* Sección de Últimos 10 Registros & Mapa de Impactos */
.recent-records-container {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.search-controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 14px;
}

.search-input-wrapper {
    position: relative;
    width: 100%;
    max-width: 380px;
}

.search-icon {
    position: absolute;
    left: 14px;
    top: 50%;
    transform: translateY(-50%);
    color: var(--text-muted);
    pointer-events: none;
}

.search-input {
    width: 100%;
    padding: 11px 16px 11px 42px;
    background: rgba(7, 12, 24, 0.85);
    border: 1px solid var(--space-border);
    border-radius: var(--radius-pill);
    color: var(--text-pure);
    font-family: var(--font-sans);
    font-size: 0.86rem;
    transition: var(--transition-fast);
}

.search-input:focus {
    border-color: var(--cyan);
    background: rgba(12, 20, 38, 0.95);
    box-shadow: 0 0 18px rgba(0, 229, 255, 0.28);
    outline: none;
}

.search-counter {
    font-family: var(--font-mono);
    font-size: 0.82rem;
    color: var(--text-muted);
}

/* Mapa Orbital de Coordenadas de Impacto */
.orbital-impact-map {
    background: rgba(7, 12, 24, 0.8);
    border: 1px solid var(--space-border);
    border-radius: var(--radius-md);
    padding: 16px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 20px;
    flex-wrap: wrap;
}

.map-radar-area {
    display: flex;
    align-items: center;
    gap: 16px;
}

.map-svg-grid {
    width: 120px;
    height: 70px;
    background: rgba(12, 20, 38, 0.6);
    border: 1px solid var(--space-border-light);
    border-radius: var(--radius-sm);
    position: relative;
    overflow: hidden;
}

.map-grid-line {
    stroke: rgba(0, 229, 255, 0.2);
    stroke-width: 1;
}

.map-target-blip {
    fill: var(--cyan);
    filter: drop-shadow(0 0 6px var(--cyan));
    transition: all 0.4s ease;
}

.map-telemetry-text {
    font-family: var(--font-mono);
    font-size: 0.78rem;
    color: var(--text-soft);
}

.map-telemetry-label {
    color: var(--cyan);
    font-weight: 700;
}

.pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 3px 10px;
    border-radius: var(--radius-pill);
    font-family: var(--font-mono);
    font-size: 0.74rem;
    font-weight: 600;
}

.pill-fell {
    background: rgba(0, 229, 255, 0.15);
    color: var(--cyan);
    border: 1px solid rgba(0, 229, 255, 0.35);
}

.pill-found {
    background: rgba(168, 85, 247, 0.15);
    color: #d8b9ff;
    border: 1px solid rgba(168, 85, 247, 0.35);
}

.missing {
    color: var(--text-dim);
    font-style: italic;
    font-size: 0.8rem;
}

/* Modal / Ficha Técnica con Apertura de Iris */
.modal-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    background: rgba(2, 4, 10, 0.8);
    backdrop-filter: blur(12px);
    display: grid;
    place-items: center;
    z-index: 1000;
    padding: 20px;
    opacity: 0;
    visibility: hidden;
    transition: var(--transition-smooth);
}

.modal-overlay.open {
    opacity: 1;
    visibility: visible;
}

.modal-sheet {
    background: linear-gradient(160deg, #0e172c 0%, #060a15 100%);
    border: 1px solid var(--cyan);
    border-radius: var(--radius-lg);
    width: 100%;
    max-width: 580px;
    padding: 30px;
    box-shadow: 0 24px 64px rgba(0, 0, 0, 0.85), 0 0 36px rgba(0, 229, 255, 0.25);
    transform: scale(0.92) translateY(14px);
    transition: var(--transition-smooth);
    position: relative;
    overflow: hidden;
}

.modal-overlay.open .modal-sheet {
    transform: scale(1) translateY(0);
}

.modal-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    border-bottom: 1px solid var(--space-border);
    padding-bottom: 16px;
    margin-bottom: 20px;
}

.modal-eyebrow {
    font-family: var(--font-mono);
    font-size: 0.74rem;
    color: var(--cyan);
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 4px;
}

.modal-title {
    margin: 0;
    font-size: 1.55rem;
    font-weight: 800;
    color: var(--text-pure);
}

.modal-close-btn {
    background: rgba(18, 29, 54, 0.8);
    border: 1px solid var(--space-border-light);
    color: var(--text-muted);
    border-radius: 50%;
    width: 36px;
    height: 36px;
    display: grid;
    place-items: center;
    cursor: pointer;
    transition: var(--transition-fast);
    padding: 0;
}

.modal-close-btn:hover {
    color: var(--text-pure);
    border-color: var(--cyan);
    background: rgba(0, 229, 255, 0.18);
    box-shadow: 0 0 12px var(--cyan);
}

.modal-fields-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 14px;
    margin-bottom: 22px;
}

.modal-field {
    background: rgba(7, 12, 24, 0.75);
    border: 1px solid var(--space-border);
    border-radius: var(--radius-sm);
    padding: 12px 14px;
    position: relative;
}

.modal-field.full-span {
    grid-column: span 2;
}

.modal-field-label {
    font-size: 0.72rem;
    font-family: var(--font-mono);
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin-bottom: 4px;
}

.modal-field-value {
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--text-pure);
}

.modal-telemetry-status {
    padding: 12px 16px;
    background: rgba(16, 185, 129, 0.12);
    border: 1px solid rgba(16, 185, 129, 0.3);
    border-radius: var(--radius-sm);
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 0.8rem;
    color: #6ee7b7;
    margin-bottom: 20px;
}

/* Nota y Metodología */
.academic-notice {
    padding: 20px;
    border-left: 4px solid var(--cyan);
    background: rgba(0, 229, 255, 0.06);
    border-radius: var(--radius-sm);
    margin: 18px 0;
    font-size: 0.9rem;
    line-height: 1.55;
    color: var(--text-soft);
}

.academic-notice strong {
    color: var(--cyan);
}

/* Pie de Página */
footer {
    border-top: 1px solid var(--space-border);
    padding-top: 24px;
    color: var(--text-muted);
    font-size: 0.82rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 14px;
}

footer a {
    color: var(--cyan);
    text-decoration: none;
    transition: var(--transition-fast);
}

footer a:hover {
    text-decoration: underline;
    color: var(--text-pure);
}

footer code {
    background: rgba(12, 20, 38, 0.9);
    padding: 3px 8px;
    border-radius: var(--radius-sm);
    border: 1px solid var(--space-border);
    color: var(--blue);
}

/* Accesibilidad: Reducción de movimiento */
@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        animation-iteration-count: 1 !important;
        transition-duration: 0.01ms !important;
        scroll-behavior: auto !important;
    }
    #space-canvas {
        display: block;
    }
    .radar-sweep-cone, .radar-orbit, .beacon-pulse, .wave-path, .donut-satellite-orbit, .kpi-spectrum span {
        animation: none !important;
    }
}

/* Adaptación Responsiva Móvil y Tablet */
@media (max-width: 1080px) {
    .kpis {
        grid-template-columns: repeat(3, 1fr);
    }
    .charts-grid {
        grid-template-columns: 1fr;
    }
    .ranking-layout {
        grid-template-columns: 1fr;
    }
    .hero-observatory {
        grid-template-columns: 1fr;
        padding: 30px 24px;
    }
    .hero-art {
        display: none;
    }
}

@media (max-width: 768px) {
    .container {
        padding: 16px 14px 60px;
    }
    .kpis {
        grid-template-columns: repeat(2, 1fr);
        gap: 12px;
    }
    .panel {
        padding: 20px 16px;
    }
    .donut-segments-interactive {
        grid-template-columns: 1fr;
    }
    .modal-fields-grid {
        grid-template-columns: 1fr;
    }
    .modal-field.full-span {
        grid-column: span 1;
    }
    .telemetry-wave-wrap {
        display: none;
    }
}

@media (max-width: 480px) {
    .kpis {
        grid-template-columns: 1fr;
    }
    h1 {
        font-size: 2rem;
    }
    .bar-row {
        grid-template-columns: 65px 1fr 50px;
        gap: 8px;
        font-size: 0.78rem;
    }
    .telemetry-bar {
        flex-direction: column;
        align-items: flex-start;
    }
}
"""


JAVASCRIPT = """
(function () {
    "use strict";

    // 1. Fondo cósmico interactivo en Canvas: Parallax multicapa, nebulosas y bólidos con chispas
    const canvas = document.querySelector("#space-canvas");
    if (canvas && canvas.getContext) {
        const ctx = canvas.getContext("2d");
        let width = (canvas.width = window.innerWidth);
        let height = (canvas.height = window.innerHeight);

        const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

        // Estrellas en tres capas de profundidad (parallax óptico)
        const starLayers = [
            { count: Math.min(70, Math.floor((width * height) / 18000)), speed: 0.05, size: [0.3, 0.9], stars: [] },
            { count: Math.min(50, Math.floor((width * height) / 24000)), speed: 0.12, size: [0.8, 1.5], stars: [] },
            { count: Math.min(25, Math.floor((width * height) / 40000)), speed: 0.25, size: [1.6, 2.4], stars: [] }
        ];

        starLayers.forEach(layer => {
            for (let i = 0; i < layer.count; i++) {
                layer.stars.push({
                    x: Math.random() * width,
                    y: Math.random() * height,
                    radius: Math.random() * (layer.size[1] - layer.size[0]) + layer.size[0],
                    baseAlpha: Math.random() * 0.6 + 0.3,
                    twinkleSpeed: Math.random() * 0.02 + 0.006,
                    phase: Math.random() * Math.PI * 2,
                    hasSpikes: Math.random() > 0.8
                });
            }
        });

        // Bólido / meteoro en curso y chispas de desintegración
        let meteor = null;
        let sparks = [];
        let lastMeteorTime = Date.now();

        // Movimiento de cursor para efecto paralaje
        let mouseX = width / 2;
        let mouseY = height / 2;
        let targetOffsetX = 0;
        let targetOffsetY = 0;
        let currentOffsetX = 0;
        let currentOffsetY = 0;

        window.addEventListener("mousemove", e => {
            mouseX = e.clientX;
            mouseY = e.clientY;
            targetOffsetX = (mouseX - width / 2) * 0.03;
            targetOffsetY = (mouseY - height / 2) * 0.03;
        });

        function spawnMeteor() {
            const startX = Math.random() * width * 0.8 + width * 0.15;
            const startY = Math.random() * (height * 0.25);
            const speed = Math.random() * 9 + 8;
            const length = Math.random() * 110 + 80;
            meteor = {
                x: startX,
                y: startY,
                vx: -speed,
                vy: speed * 0.58,
                length: length,
                alpha: 1,
            };
            lastMeteorTime = Date.now();
        }

        function drawSpace() {
            ctx.clearRect(0, 0, width, height);

            currentOffsetX += (targetOffsetX - currentOffsetX) * 0.05;
            currentOffsetY += (targetOffsetY - currentOffsetY) * 0.05;

            // Dibujar nebulosa cósmica sutil
            const gradNebula = ctx.createRadialGradient(
                width * 0.85 + currentOffsetX * 0.5, height * 0.15 + currentOffsetY * 0.5, 40,
                width * 0.85, height * 0.15, Math.max(width * 0.45, 300)
            );
            gradNebula.addColorStop(0, "rgba(0, 229, 255, 0.04)");
            gradNebula.addColorStop(0.5, "rgba(168, 85, 247, 0.03)");
            gradNebula.addColorStop(1, "rgba(3, 6, 15, 0)");
            ctx.fillStyle = gradNebula;
            ctx.fillRect(0, 0, width, height);

            // Dibujar capas de estrellas con paralaje
            starLayers.forEach(layer => {
                const offX = currentOffsetX * layer.speed;
                const offY = currentOffsetY * layer.speed;

                for (let i = 0; i < layer.stars.length; i++) {
                    const s = layer.stars[i];
                    let alpha = s.baseAlpha;
                    if (!prefersReducedMotion) {
                        s.phase += s.twinkleSpeed;
                        alpha = s.baseAlpha + Math.sin(s.phase) * 0.25;
                        alpha = Math.max(0.15, Math.min(1, alpha));
                    }

                    const renderX = (s.x + offX + width) % width;
                    const renderY = (s.y + offY + height) % height;

                    ctx.beginPath();
                    ctx.arc(renderX, renderY, s.radius, 0, Math.PI * 2);
                    ctx.fillStyle = "rgba(240, 246, 255, " + alpha + ")";
                    ctx.fill();

                    // Picos de difracción de telescopio en estrellas brillantes
                    if (s.hasSpikes && alpha > 0.6) {
                        ctx.strokeStyle = "rgba(0, 229, 255, " + (alpha * 0.4) + ")";
                        ctx.lineWidth = 0.8;
                        ctx.beginPath();
                        ctx.moveTo(renderX - s.radius * 3.5, renderY);
                        ctx.lineTo(renderX + s.radius * 3.5, renderY);
                        ctx.moveTo(renderX, renderY - s.radius * 3.5);
                        ctx.lineTo(renderX, renderY + s.radius * 3.5);
                        ctx.stroke();
                    }
                }
            });

            // Dibujar bólido y chispas
            if (!prefersReducedMotion) {
                if (meteor) {
                    ctx.save();
                    const tailX = meteor.x - (meteor.vx / 10) * meteor.length;
                    const tailY = meteor.y - (meteor.vy / 10) * meteor.length;

                    const grad = ctx.createLinearGradient(meteor.x, meteor.y, tailX, tailY);
                    grad.addColorStop(0, "rgba(255, 255, 255, " + meteor.alpha + ")");
                    grad.addColorStop(0.15, "rgba(0, 229, 255, " + (meteor.alpha * 0.9) + ")");
                    grad.addColorStop(0.5, "rgba(168, 85, 247, " + (meteor.alpha * 0.5) + ")");
                    grad.addColorStop(1, "rgba(255, 255, 255, 0)");

                    ctx.strokeStyle = grad;
                    ctx.lineWidth = 2.2;
                    ctx.beginPath();
                    ctx.moveTo(meteor.x, meteor.y);
                    ctx.lineTo(tailX, tailY);
                    ctx.stroke();

                    // Núcleo brillante
                    ctx.fillStyle = "rgba(255, 255, 255, " + meteor.alpha + ")";
                    ctx.beginPath();
                    ctx.arc(meteor.x, meteor.y, 2.5, 0, Math.PI * 2);
                    ctx.fill();

                    ctx.restore();

                    // Generar microchispas detrás del bólido
                    if (Math.random() > 0.4) {
                        sparks.push({
                            x: meteor.x + (Math.random() - 0.5) * 6,
                            y: meteor.y + (Math.random() - 0.5) * 6,
                            vx: (Math.random() - 0.5) * 2,
                            vy: (Math.random() - 0.5) * 2,
                            alpha: 0.8,
                            size: Math.random() * 1.5 + 0.5
                        });
                    }

                    meteor.x += meteor.vx;
                    meteor.y += meteor.vy;
                    meteor.alpha -= 0.016;

                    if (meteor.alpha <= 0 || meteor.x < -100 || meteor.y > height + 100) {
                        meteor = null;
                    }
                } else if (Date.now() - lastMeteorTime > 7000 + Math.random() * 5000) {
                    spawnMeteor();
                }

                // Animar y dibujar chispas de fricción atmosférica
                for (let i = sparks.length - 1; i >= 0; i--) {
                    const sp = sparks[i];
                    ctx.fillStyle = "rgba(0, 229, 255, " + sp.alpha + ")";
                    ctx.beginPath();
                    ctx.arc(sp.x, sp.y, sp.size, 0, Math.PI * 2);
                    ctx.fill();

                    sp.x += sp.vx;
                    sp.y += sp.vy;
                    sp.alpha -= 0.03;
                    if (sp.alpha <= 0) sparks.splice(i, 1);
                }

                requestAnimationFrame(drawSpace);
            }
        }

        window.addEventListener("resize", function () {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
            if (prefersReducedMotion) drawSpace();
        });

        drawSpace();
    }

    // 2. Rastreador dinámico de coordenadas del telescopio (coordenadas ecuatoriales)
    const coordDisplay = document.querySelector("#telescope-coords-val");
    if (coordDisplay) {
        window.addEventListener("mousemove", e => {
            const raHours = Math.floor((e.clientX / window.innerWidth) * 24);
            const raMin = Math.floor(((e.clientX / window.innerWidth) * 1440) % 60);
            const decDeg = Math.floor((e.clientY / window.innerHeight) * 90) - 20;
            const azDeg = ((e.clientX + e.clientY) % 360).toFixed(1);
            coordDisplay.textContent = `RA ${raHours}h ${raMin}m · DEC ${decDeg >= 0 ? "+" : ""}${decDeg}° · AZ ${azDeg}°`;
        });
    }

    // 3. Modos interactivos del escáner de radar (Óptico / Radar / Infrarrojo)
    const modeBtns = document.querySelectorAll(".scan-mode-btn");
    const radarCone = document.querySelector(".radar-sweep-cone");
    modeBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            modeBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");
            const mode = btn.getAttribute("data-mode");
            if (radarCone) {
                if (mode === "infrared") {
                    radarCone.setAttribute("fill", "url(#radar-sweep-amber)");
                } else if (mode === "optical") {
                    radarCone.setAttribute("fill", "url(#radar-sweep-purple)");
                } else {
                    radarCone.setAttribute("fill", "url(#radar-sweep-cyan)");
                }
            }
        });
    });

    // 4. Animación de contadores numéricos en tarjetas KPI
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const counters = document.querySelectorAll(".kpi-value[data-target]");

    function animarContador(elem) {
        const raw = elem.getAttribute("data-target");
        if (!raw) return;
        const target = parseFloat(raw);
        if (isNaN(target)) return;

        if (prefersReducedMotion) return;

        const isFloat = raw.includes(".");
        const decimals = isFloat ? 2 : 0;
        const duration = 1200;
        const start = performance.now();

        function update(now) {
            const progress = Math.min((now - start) / duration, 1);
            const ease = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
            const current = target * ease;

            let texto = current.toLocaleString("es-ES", {
                minimumFractionDigits: decimals,
                maximumFractionDigits: decimals,
            });

            if (decimals > 0 && elem.textContent.includes("g")) {
                elem.textContent = texto + " g";
            } else {
                elem.textContent = texto;
            }

            if (progress < 1) {
                requestAnimationFrame(update);
            }
        }

        requestAnimationFrame(update);
    }

    counters.forEach(animarContador);

    // 5. Control de tooltips en tarjetas KPI
    const tooltipBtns = document.querySelectorAll(".kpi-info-btn");
    tooltipBtns.forEach(btn => {
        btn.addEventListener("click", e => {
            e.stopPropagation();
            const expanded = btn.getAttribute("aria-expanded") === "true";
            tooltipBtns.forEach(b => b.setAttribute("aria-expanded", "false"));
            btn.setAttribute("aria-expanded", String(!expanded));
        });
    });

    document.addEventListener("click", () => {
        tooltipBtns.forEach(b => b.setAttribute("aria-expanded", "false"));
    });

    // 6. Gráfico interactivo Top 10 Clasificaciones
    const barRows = document.querySelectorAll(".bar-row");
    const hudClase = document.querySelector("#hud-clase-nombre");
    const hudCantidad = document.querySelector("#hud-clase-cant");
    const hudPorcentaje = document.querySelector("#hud-clase-pct");

    function seleccionarClase(row) {
        barRows.forEach(r => r.classList.remove("active"));
        row.classList.add("active");
        const clase = row.getAttribute("data-clase") || "";
        const cant = row.getAttribute("data-cantidad") || "";
        const pct = row.getAttribute("data-porcentaje") || "";

        if (hudClase) hudClase.textContent = clase;
        if (hudCantidad) hudCantidad.textContent = cant + " meteoritos";
        if (hudPorcentaje) hudPorcentaje.textContent = pct;
    }

    barRows.forEach(row => {
        row.addEventListener("mouseenter", () => seleccionarClase(row));
        row.addEventListener("focus", () => seleccionarClase(row));
        row.addEventListener("click", () => seleccionarClase(row));
        row.addEventListener("keydown", e => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                seleccionarClase(row);
            }
        });
    });

    // 7. Gráfico interactivo Fell vs Found
    const fellCard = document.querySelector("#card-fell");
    const foundCard = document.querySelector("#card-found");
    const donutRing = document.querySelector(".donut-ring");
    const donutValor = document.querySelector("#donut-val");
    const donutEtiqueta = document.querySelector("#donut-lbl");
    const donutHUD = document.querySelector("#donut-hud-texto");

    const totalFell = donutRing ? donutRing.getAttribute("data-fell-count") : "";
    const pctFell = donutRing ? donutRing.getAttribute("data-fell-pct") : "";
    const totalFound = donutRing ? donutRing.getAttribute("data-found-count") : "";
    const pctFound = donutRing ? donutRing.getAttribute("data-found-pct") : "";
    const totalGral = donutRing ? donutRing.getAttribute("data-total") : "";

    function destacarTipo(tipo) {
        if (!donutValor || !donutEtiqueta || !donutHUD) return;
        if (tipo === "fell") {
            if (fellCard) fellCard.classList.add("active");
            if (foundCard) foundCard.classList.remove("active");
            donutValor.textContent = totalFell;
            donutEtiqueta.textContent = "Fell (" + pctFell + "%)";
            donutHUD.innerHTML = '<span style="color:var(--cyan);font-weight:700;">Caída atestiguada:</span> Impacto observado y recuperado poco después de la entrada atmosférica.';
        } else if (tipo === "found") {
            if (foundCard) foundCard.classList.add("active");
            if (fellCard) fellCard.classList.remove("active");
            donutValor.textContent = totalFound;
            donutEtiqueta.textContent = "Found (" + pctFound + "%)";
            donutHUD.innerHTML = '<span style="color:var(--purple);font-weight:700;">Hallazgo en superficie:</span> Espécimen descubierto casualmente o en prospecciones geológicas.';
        } else {
            if (fellCard) fellCard.classList.remove("active");
            if (foundCard) foundCard.classList.remove("active");
            donutValor.textContent = totalGral;
            donutEtiqueta.textContent = "meteoritos";
            donutHUD.textContent = "Selecciona Fell o Found para examinar su proporción y significado geológico.";
        }
    }

    if (fellCard) {
        fellCard.addEventListener("mouseenter", () => destacarTipo("fell"));
        fellCard.addEventListener("focus", () => destacarTipo("fell"));
        fellCard.addEventListener("click", () => destacarTipo("fell"));
    }
    if (foundCard) {
        foundCard.addEventListener("mouseenter", () => destacarTipo("found"));
        foundCard.addEventListener("focus", () => destacarTipo("found"));
        foundCard.addEventListener("click", () => destacarTipo("found"));
    }

    // 8. Ranking de masas con Spotlight interactivo
    const rankingFilas = document.querySelectorAll(".ranking-row");
    const spotRank = document.querySelector("#spotlight-rank-val");
    const spotNombre = document.querySelector("#spotlight-nombre-val");
    const spotId = document.querySelector("#spotlight-id-val");
    const spotGramos = document.querySelector("#spotlight-g-val");
    const spotKg = document.querySelector("#spotlight-kg-val");
    const spotTon = document.querySelector("#spotlight-ton-val");
    const spotBar = document.querySelector("#spotlight-scale-bar");
    const spotPct = document.querySelector("#spotlight-scale-pct");

    function actualizarSpotlight(fila) {
        rankingFilas.forEach(f => f.classList.remove("selected-row"));
        fila.classList.add("selected-row");

        const rank = fila.getAttribute("data-rank") || "#1";
        const nombre = fila.getAttribute("data-nombre") || "";
        const id = fila.getAttribute("data-id") || "";
        const masaG = fila.getAttribute("data-masa-g") || "";
        const masaKg = fila.getAttribute("data-masa-kg") || "";
        const masaTon = fila.getAttribute("data-masa-ton") || "";
        const pctRelativo = fila.getAttribute("data-pct-rel") || "100%";

        if (spotRank) spotRank.textContent = rank;
        if (spotNombre) spotNombre.textContent = nombre;
        if (spotId) spotId.textContent = "ID Catálogo NASA: " + id;
        if (spotGramos) spotGramos.textContent = masaG + " g";
        if (spotKg) spotKg.textContent = masaKg;
        if (spotTon) spotTon.textContent = masaTon;
        if (spotBar) spotBar.style.width = pctRelativo;
        if (spotPct) spotPct.textContent = pctRelativo + " respecto al líder";
    }

    rankingFilas.forEach(fila => {
        fila.addEventListener("mouseenter", () => actualizarSpotlight(fila));
        fila.addEventListener("focus", () => actualizarSpotlight(fila));
        fila.addEventListener("click", () => actualizarSpotlight(fila));
        fila.addEventListener("keydown", e => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                actualizarSpotlight(fila);
            }
        });
    });

    // 9. Buscador y Mapa de impacto para los últimos diez registros
    const buscador = document.querySelector("#buscador");
    const filasRecientes = document.querySelectorAll("#recientes-tabla tbody tr.fila-reciente");
    const contador = document.querySelector("#filas-visibles");
    const mapTargetBlip = document.querySelector("#map-target-blip");
    const mapTargetText = document.querySelector("#map-target-text");

    if (buscador) {
        buscador.addEventListener("input", () => {
            const texto = buscador.value.toLowerCase().trim();
            let visibles = 0;

            filasRecientes.forEach(fila => {
                const coincide = fila.textContent.toLowerCase().includes(texto);
                fila.hidden = !coincide;
                if (coincide) visibles++;
            });

            if (contador) {
                contador.textContent = `${visibles} de ${filasRecientes.length} registros visibles`;
            }
        });
    }

    function proyectarEnMapa(fila) {
        const rawJson = fila.getAttribute("data-record");
        if (!rawJson) return;
        try {
            const data = JSON.parse(rawJson);
            const lat = parseFloat(data.lat);
            const long = parseFloat(data.long);

            if (!isNaN(lat) && !isNaN(long) && mapTargetBlip) {
                // Proyección cartesiana simple sobre el minirradar (120x70)
                const px = Math.max(8, Math.min(112, ((long + 180) / 360) * 120));
                const py = Math.max(8, Math.min(62, ((-lat + 90) / 180) * 70));
                mapTargetBlip.setAttribute("cx", px);
                mapTargetBlip.setAttribute("cy", py);

                const latHem = lat >= 0 ? "N" : "S";
                const lonHem = long >= 0 ? "E" : "W";
                if (mapTargetText) {
                    mapTargetText.innerHTML = `<span class="map-telemetry-label">${escape(data.name)}:</span> ${Math.abs(lat).toFixed(2)}° ${latHem}, ${Math.abs(long).toFixed(2)}° ${lonHem} [COORDENADAS BLOQUEADAS]`;
                }
            } else if (mapTargetText) {
                mapTargetText.innerHTML = `<span class="map-telemetry-label">${escape(data.name)}:</span> Sin coordenadas registradas en la NASA.`;
            }
        } catch (e) {
            console.error(e);
        }
    }

    filasRecientes.forEach(fila => {
        fila.addEventListener("mouseenter", () => proyectarEnMapa(fila));
        fila.addEventListener("focus", () => proyectarEnMapa(fila));
    });

    // 10. Ficha Técnica / Modal accesible al hacer clic en filas recientes
    const modal = document.querySelector("#modal-ficha");
    const modalCerrar = document.querySelector("#modal-cerrar-btn");
    const modalNombre = document.querySelector("#modal-val-nombre");
    const modalId = document.querySelector("#modal-val-id");
    const modalClase = document.querySelector("#modal-val-clase");
    const modalMasa = document.querySelector("#modal-val-masa");
    const modalTipo = document.querySelector("#modal-val-tipo");
    const modalAnio = document.querySelector("#modal-val-anio");
    const modalCoord = document.querySelector("#modal-val-coord");

    let elementoPrevio = null;

    function abrirModal(fila) {
        elementoPrevio = fila;
        const rawJson = fila.getAttribute("data-record");
        if (!rawJson) return;

        try {
            const data = JSON.parse(rawJson);

            if (modalNombre) modalNombre.textContent = data.name || "Sin nombre";
            if (modalId) modalId.textContent = "ID Oficial: " + (data.id || "N/D");
            if (modalClase) modalClase.textContent = data.recclass || "Sin clasificar";

            // Formateo de masa con manejo de faltantes
            if (modalMasa) {
                if (data.mass && data.mass.trim() !== "") {
                    const numMasa = parseFloat(data.mass);
                    const formattedG = isNaN(numMasa) ? data.mass : numMasa.toLocaleString("es-ES") + " g";
                    const formattedKg = isNaN(numMasa) ? "" : " (" + (numMasa / 1000).toLocaleString("es-ES", { maximumFractionDigits: 3 }) + " kg)";
                    modalMasa.innerHTML = `<span style="color:var(--cyan);font-weight:700;">${formattedG}${formattedKg}</span>`;
                } else {
                    modalMasa.innerHTML = '<span class="missing">Sin información de masa (excluida del cálculo de media)</span>';
                }
            }

            // Tipo Fell / Found
            if (modalTipo) {
                if (data.fall === "Fell") {
                    modalTipo.innerHTML = '<span class="pill pill-fell">Caída observada (Fell)</span>';
                } else {
                    modalTipo.innerHTML = '<span class="pill pill-found">Hallazgo terrestre (Found)</span>';
                }
            }

            // Año con manejo de faltantes
            if (modalAnio) {
                const anioLimpio = data.year ? data.year.substring(0, 4) : "";
                modalAnio.innerHTML = anioLimpio ? anioLimpio : '<span class="missing">Año no registrado</span>';
            }

            // Coordenadas con formato geográfico
            if (modalCoord) {
                const lat = data.lat ? data.lat.trim() : "";
                const long = data.long ? data.long.trim() : "";
                if (lat && long) {
                    const latNum = parseFloat(lat);
                    const longNum = parseFloat(long);
                    const latHemisferio = latNum >= 0 ? "N" : "S";
                    const longHemisferio = longNum >= 0 ? "E" : "W";
                    modalCoord.textContent = `${Math.abs(latNum).toFixed(4)}° ${latHemisferio}, ${Math.abs(longNum).toFixed(4)}° ${longHemisferio}`;
                } else {
                    modalCoord.innerHTML = '<span class="missing">Sin coordenadas registradas</span>';
                }
            }

            if (modal) {
                modal.classList.add("open");
                modal.setAttribute("aria-hidden", "false");
                if (modalCerrar) modalCerrar.focus();
            }
        } catch (err) {
            console.error("Error al analizar registro:", err);
        }
    }

    function cerrarModal() {
        if (modal) {
            modal.classList.remove("open");
            modal.setAttribute("aria-hidden", "true");
        }
        if (elementoPrevio) {
            elementoPrevio.focus();
        }
    }

    filasRecientes.forEach(fila => {
        fila.addEventListener("click", () => abrirModal(fila));
        fila.addEventListener("keydown", e => {
            if (e.key === "Enter" || e.key === " ") {
                e.preventDefault();
                abrirModal(fila);
            }
        });
    });

    if (modalCerrar) {
        modalCerrar.addEventListener("click", cerrarModal);
    }

    if (modal) {
        modal.addEventListener("click", e => {
            if (e.target === modal) cerrarModal();
        });
    }

    document.addEventListener("keydown", e => {
        if (e.key === "Escape" && modal && modal.classList.contains("open")) {
            cerrarModal();
        }
    });

})();
"""


def crear_html(indicadores, commit="LOCAL"):
    """Genera la página HTML completa del observatorio de meteoritos."""
    total = indicadores["total"]
    fell = indicadores["fell"]
    found = indicadores["found"]
    sin_masa = indicadores["sin_masa"]
    media = indicadores["masa_media"]

    porcentaje_fell = (fell / total * 100) if total else 0
    porcentaje_found = (found / total * 100) if total else 0
    porcentaje_faltante = (sin_masa / total * 100) if total else 0

    grados_fell = (porcentaje_fell / 100) * 360

    fecha = datetime.now(timezone.utc).strftime("%d/%m/%Y %H:%M UTC")

    # 1. Tarjetas KPI
    tarjetas = "".join([
        tarjeta_kpi(
            "total",
            "Meteoritos registrados",
            formato(total),
            total,
            "Total Catálogo",
            "Registros validados del CSV versionado",
            "Catálogo global analizado",
            "Filas válidas",
            "Conteo de registros válidos, incluidas las simulaciones educativas.",
            "OBS-01"
        ),
        tarjeta_kpi(
            "fell",
            "Caídas observadas",
            formato(fell),
            fell,
            "Fell",
            f"{porcentaje_fell:.2f}% de la muestra",
            "Caídas atestiguadas en tiempo real",
            "Meteoritos avistados",
            "(Fell / Total) × 100. Casos con observación ocular del bólido antes de su impacto.",
            "OBS-02"
        ),
        tarjeta_kpi(
            "found",
            "Hallazgos en superficie",
            formato(found),
            found,
            "Found",
            f"{porcentaje_found:.2f}% de la muestra",
            "Descubrimientos terrestres posteriores",
            "Meteoritos hallados",
            "(Found / Total) × 100. Localizados en expediciones (desiertos, hielos) sin avistamiento.",
            "OBS-03"
        ),
        tarjeta_kpi(
            "media",
            "Masa media",
            formato(media, 2) + " g" if media is not None else "N/D",
            media,
            "Media (g)",
            f"{formato(media / 1000, 2) + ' kg' if media is not None else 'N/D'} por espécimen",
            "Promedio aritmético de masa",
            "Gramos (g)",
            "Calculada exclusivamente sobre registros con masa válida; los faltantes se omiten sin imputar 0.",
            "OBS-04"
        ),
        tarjeta_kpi(
            "sin_masa",
            "Sin información de masa",
            formato(sin_masa),
            sin_masa,
            "Faltantes",
            f"{porcentaje_faltante:.2f}% de registros incompletos",
            "Registros con campo de masa vacío",
            "Muestras sin pesar",
            "(Sin masa / Total) × 100. Identifica lagunas de datos en el archivo histórico de la NASA.",
            "OBS-05"
        )
    ])

    # 2. Gráfico interactivo Top 10 Clasificaciones
    clases = indicadores["top_clasificaciones"]
    maximo = max((cantidad for _, cantidad in clases), default=1)
    primera_clase = clases[0][0] if clases else "N/D"
    primera_cant = clases[0][1] if clases else 0
    primera_pct = (primera_cant / total * 100) if total else 0

    barras = ""
    for clase, cantidad in clases:
        ancho = (cantidad / maximo * 100) if maximo else 0
        pct = (cantidad / total * 100) if total else 0
        barras += f"""
        <div class="bar-row" tabindex="0" role="listitem"
             aria-label="Clase {seguro(clase)}: {formato(cantidad)} meteoritos ({pct:.2f}% del catálogo)"
             data-clase="{seguro(clase)}" data-cantidad="{formato(cantidad)}" data-porcentaje="{pct:.2f}%">
            <span class="bar-label">{seguro(clase)}</span>
            <div class="bar-track">
                <span class="bar-fill" style="width:{ancho:.2f}%"></span>
            </div>
            <span class="bar-value">{formato(cantidad)}</span>
        </div>
        """

    # 3. Ranking de los 10 meteoritos más pesados
    ranking_filas = ""
    primer_lider = None
    max_masa_ranking = indicadores["ranking_masas"][0]["masa_g"] if indicadores["ranking_masas"] else 1

    for posicion, meteorito in enumerate(indicadores["ranking_masas"], start=1):
        masa_g = meteorito["masa_g"]
        kg_str, ton_str = formato_metricas_masa(masa_g)
        pct_rel = (masa_g / max_masa_ranking * 100) if max_masa_ranking else 100
        clase_rank = "rank-badge rank-top-1" if posicion == 1 else "rank-badge"
        clase_fila = "ranking-row selected-row" if posicion == 1 else "ranking-row"

        if posicion == 1:
            primer_lider = {
                "rank": f"#{posicion}",
                "name": seguro(meteorito["name"]),
                "id": seguro(meteorito["id"]),
                "masa_g": formato(masa_g, 2),
                "kg": kg_str,
                "ton": ton_str,
                "pct_rel": f"{pct_rel:.1f}%"
            }

        ranking_filas += f"""
        <tr class="{clase_fila}" tabindex="0" role="row"
            data-rank="#{posicion}" data-nombre="{seguro(meteorito['name'])}"
            data-id="{seguro(meteorito['id'])}" data-masa-g="{formato(masa_g, 2)}"
            data-masa-kg="{seguro(kg_str)}" data-masa-ton="{seguro(ton_str)}"
            data-pct-rel="{pct_rel:.1f}%">
            <td><span class="{clase_rank}">#{posicion}</span></td>
            <td><strong>{seguro(meteorito['name'])}</strong></td>
            <td><code>{seguro(meteorito['id'])}</code></td>
            <td style="font-family:var(--font-mono);">{formato(masa_g, 2)}</td>
        </tr>
        """

    if not primer_lider:
        primer_lider = {
            "rank": "#1", "name": "N/D", "id": "0", "masa_g": "0,00",
            "kg": "0,00 kg", "ton": "0,00 t", "pct_rel": "100%"
        }

    # 4. Últimos diez registros conservando el orden exacto del CSV
    recientes = ""
    for registro in indicadores["ultimos_registros"]:
        tipo = registro["fall"].strip()
        clase_pill = "pill-fell" if tipo == "Fell" else "pill-found"
        json_attr = serializar_registro(registro)

        recientes += f"""
        <tr class="fila-reciente" tabindex="0" role="button"
            aria-haspopup="dialog" aria-label="Abrir ficha técnica de {seguro(registro['name'])}"
            data-record="{json_attr}">
            <td><code>{mostrar(registro['id'])}</code></td>
            <td><strong>{mostrar(registro['name'])}</strong></td>
            <td><span class="bar-label">{mostrar(registro['recclass'])}</span></td>
            <td style="font-family:var(--font-mono);">{mostrar(registro['mass (g)'])}</td>
            <td><span class="pill {clase_pill}">{seguro(tipo)}</span></td>
            <td>{mostrar(registro['year'])}</td>
            <td style="font-family:var(--font-mono);">{mostrar(registro['reclat'])}</td>
            <td style="font-family:var(--font-mono);">{mostrar(registro['reclong'])}</td>
        </tr>
        """

    # Construcción del documento HTML con diseño espacial optimizado
    return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description"
          content="Centro de Control y Observatorio de Meteoritos NASA. Telemetría de {formato(total)} registros procesados mediante CI/CD y Python.">
    <title>Meteorite Observatory | CI/CD</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>{ESTILOS}</style>
</head>
<body>

<canvas id="space-canvas" aria-hidden="true"></canvas>

<div class="container">

    <header>
        <div class="telemetry-bar">
            <div class="telemetry-status">
                <div class="beacon-pulse-group" aria-hidden="true">
                    <span class="beacon-core"></span>
                    <span class="beacon-pulse"></span>
                </div>
                <span>OBSERVATORIO OPERATIVO // TELEMETRÍA CI/CD</span>
            </div>

            <div class="telemetry-wave-wrap" aria-hidden="true">
                <svg class="telemetry-waveform" viewBox="0 0 160 24" fill="none">
                    <path class="wave-path" d="M0,12 L30,12 L38,4 L46,20 L54,12 L70,12 L78,2 L86,22 L94,12 L120,12 L128,6 L136,18 L144,12 L160,12" />
                </svg>
                <span style="font-size:0.75rem;letter-spacing:1px;color:var(--cyan);">SEÑAL ACTIVA</span>
            </div>

            <div class="telemetry-meta">
                <span class="telescope-coords" id="telescope-coords-val">RA 18h 36m · DEC +38° 47′ · AZ 142.4°</span>
                <span class="telemetry-item">FECHA: <span>{seguro(fecha)}</span></span>
                <span class="telemetry-item">COMMIT: <code>{seguro(commit)}</code></span>
            </div>
        </div>

        <section class="hero-observatory">
            <span class="corner-bracket corner-tl" aria-hidden="true"></span>
            <span class="corner-bracket corner-tr" aria-hidden="true"></span>
            <span class="corner-bracket corner-bl" aria-hidden="true"></span>
            <span class="corner-bracket corner-br" aria-hidden="true"></span>

            <div class="hero-content">
                <div class="eyebrow">
                    <span class="eyebrow-dot" aria-hidden="true"></span>
                    NASA OPEN DATA · CENTRO DE CONTROL PLANETARIO
                </div>
                <h1>Meteorite Observatory</h1>
                <p class="subtitle">
                    Exploración analítica de {formato(total)} impactos y hallazgos de meteoritos en la Tierra.
                    Validación exhaustiva de integridad con Python y entrega continua en GitHub Actions.
                </p>
                <div class="hero-tags">
                    <span class="hero-tag">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                            <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
                        </svg>
                        Ingeniería en Ciencia de Datos
                    </span>
                    <span class="hero-tag">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                        </svg>
                        Muestra: {formato(total)} especímenes
                    </span>
                    <span class="hero-tag">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                        </svg>
                        Pipeline CI/CD 100% Verificado
                    </span>
                </div>
            </div>

            <div class="hero-art" aria-hidden="true">
                <div class="radar-console">
                    <svg class="radar-art-svg" viewBox="0 0 300 300" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <!-- Anillos de alcance de detección -->
                        <circle cx="150" cy="150" r="135" stroke="#1a2947" stroke-width="1.5" stroke-dasharray="4 4" />
                        <circle cx="150" cy="150" r="95" stroke="#283e68" stroke-width="1.5" />
                        <circle cx="150" cy="150" r="55" stroke="#00e5ff" stroke-width="1.2" stroke-opacity="0.35" />
                        <!-- Ejes cartesianos -->
                        <line x1="150" y1="12" x2="150" y2="288" stroke="#1a2947" stroke-width="1.2" />
                        <line x1="12" y1="150" x2="288" y2="150" stroke="#1a2947" stroke-width="1.2" />
                        <!-- Haz giratorio de radar -->
                        <g class="radar-sweep-cone" fill="url(#radar-sweep-cyan)">
                            <path d="M150,150 L285,150 A135,135 0 0,0 245,55 Z" opacity="0.6" />
                        </g>
                        <!-- Puntos de meteoritos detectados con pulso -->
                        <circle class="radar-blip blip-1" cx="210" cy="95" r="4.5" fill="#00e5ff" />
                        <circle class="radar-blip blip-2" cx="80" cy="190" r="4" fill="#a855f7" />
                        <circle class="radar-blip blip-3" cx="195" cy="220" r="4" fill="#f59e0b" />
                        <!-- Órbita elíptica de asteroide -->
                        <g class="radar-orbit">
                            <ellipse cx="150" cy="150" rx="120" ry="46" stroke="url(#orbit-grad)" stroke-width="2" transform="rotate(-32 150 150)" />
                            <circle cx="255" cy="100" r="5.5" fill="#00e5ff" filter="drop-shadow(0 0 8px #00e5ff)" />
                        </g>
                        <defs>
                            <linearGradient id="radar-sweep-cyan" x1="150" y1="150" x2="285" y2="100">
                                <stop offset="0%" stop-color="#00e5ff" stop-opacity="0.7" />
                                <stop offset="100%" stop-color="#00e5ff" stop-opacity="0" />
                            </linearGradient>
                            <linearGradient id="radar-sweep-purple" x1="150" y1="150" x2="285" y2="100">
                                <stop offset="0%" stop-color="#a855f7" stop-opacity="0.7" />
                                <stop offset="100%" stop-color="#a855f7" stop-opacity="0" />
                            </linearGradient>
                            <linearGradient id="radar-sweep-amber" x1="150" y1="150" x2="285" y2="100">
                                <stop offset="0%" stop-color="#f59e0b" stop-opacity="0.7" />
                                <stop offset="100%" stop-color="#f59e0b" stop-opacity="0" />
                            </linearGradient>
                            <linearGradient id="orbit-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                                <stop offset="0%" stop-color="#00e5ff" stop-opacity="0.8" />
                                <stop offset="50%" stop-color="#a855f7" stop-opacity="0.4" />
                                <stop offset="100%" stop-color="#38bdf8" stop-opacity="0.1" />
                            </linearGradient>
                        </defs>
                    </svg>
                </div>
                <div class="scanner-controls">
                    <button type="button" class="scan-mode-btn active" data-mode="radar" aria-label="Modo Radar">[RADAR]</button>
                    <button type="button" class="scan-mode-btn" data-mode="optical" aria-label="Modo Óptico">[ÓPTICO]</button>
                    <button type="button" class="scan-mode-btn" data-mode="infrared" aria-label="Modo Infrarrojo">[INFRARROJO]</button>
                </div>
            </div>
        </section>
    </header>

    <section class="kpis" aria-label="Indicadores principales de la muestra">
        {tarjetas}
    </section>

    <section class="charts-grid">
        <article class="panel" id="panel-clases">
            <span class="corner-bracket corner-tl" aria-hidden="true"></span>
            <span class="corner-bracket corner-tr" aria-hidden="true"></span>
            <span class="corner-bracket corner-bl" aria-hidden="true"></span>
            <span class="corner-bracket corner-br" aria-hidden="true"></span>

            <div class="panel-header">
                <div class="panel-title-area">
                    <h2>
                        <span class="panel-icon-dot" aria-hidden="true"></span>
                        Top 10 clasificaciones
                    </h2>
                    <p class="panel-desc">Frecuencia por clase petrológica y mineralógica de meteorito.</p>
                </div>
            </div>
            <div class="bar-chart-container" role="list" aria-label="Gráfico interactivo de las diez clases más comunes">
                {barras}
            </div>
            <div class="chart-inspector-hud" id="clase-hud" aria-live="polite">
                <span>Enfoque: <strong class="hud-highlight" id="hud-clase-nombre">{seguro(primera_clase)}</strong></span>
                <span>Frecuencia: <strong class="hud-highlight" id="hud-clase-cant">{formato(primera_cant)} meteoritos</strong></span>
                <span>Proporción: <strong class="hud-highlight" id="hud-clase-pct">{primera_pct:.2f}%</strong></span>
            </div>
        </article>

        <article class="panel" id="panel-tipo">
            <span class="corner-bracket corner-tl" aria-hidden="true"></span>
            <span class="corner-bracket corner-tr" aria-hidden="true"></span>
            <span class="corner-bracket corner-bl" aria-hidden="true"></span>
            <span class="corner-bracket corner-br" aria-hidden="true"></span>

            <div class="panel-header">
                <div class="panel-title-area">
                    <h2>
                        <span class="panel-icon-dot" aria-hidden="true"></span>
                        Tipo de registro
                    </h2>
                    <p class="panel-desc">Comparativa entre caídas avistadas y hallazgos en terreno.</p>
                </div>
            </div>
            <div class="donut-container">
                <div class="donut-graphic-wrapper">
                    <div class="donut-satellite-orbit" aria-hidden="true">
                        <span class="donut-satellite-dot"></span>
                    </div>
                    <div class="donut-ring"
                         style="--fell-deg:{grados_fell:.3f}deg;"
                         data-fell-count="{formato(fell)}"
                         data-fell-pct="{porcentaje_fell:.2f}"
                         data-found-count="{formato(found)}"
                         data-found-pct="{porcentaje_found:.2f}"
                         data-total="{formato(total)}"
                         role="img"
                         aria-label="Gráfico circular: Fell {porcentaje_fell:.2f} por ciento; Found {porcentaje_found:.2f} por ciento">
                        <div class="donut-core">
                            <strong id="donut-val">{formato(total)}</strong>
                            <small id="donut-lbl">meteoritos</small>
                        </div>
                    </div>
                </div>

                <div class="donut-segments-interactive">
                    <button type="button" class="segment-card fell-card" id="card-fell" tabindex="0">
                        <div class="segment-header">
                            <span class="segment-dot dot-cyan" aria-hidden="true"></span>
                            <span>Fell (Caídas)</span>
                        </div>
                        <div class="segment-stat">{formato(fell)} ({porcentaje_fell:.2f}%)</div>
                        <div class="segment-desc">Observados en descenso directo antes del rescate.</div>
                    </button>

                    <button type="button" class="segment-card found-card" id="card-found" tabindex="0">
                        <div class="segment-header">
                            <span class="segment-dot dot-purple" aria-hidden="true"></span>
                            <span>Found (Hallazgos)</span>
                        </div>
                        <div class="segment-stat">{formato(found)} ({porcentaje_found:.2f}%)</div>
                        <div class="segment-desc">Descubiertos en superficie sin avistamiento previo.</div>
                    </button>
                </div>

                <div class="chart-inspector-hud" style="width:100%;margin-top:14px;" id="donut-hud-texto">
                    Pasa el cursor o selecciona Fell o Found para examinar su proporción y significado geológico.
                </div>
            </div>
        </article>
    </section>

    <section class="panel" id="ranking-panel">
        <span class="corner-bracket corner-tl" aria-hidden="true"></span>
        <span class="corner-bracket corner-tr" aria-hidden="true"></span>
        <span class="corner-bracket corner-bl" aria-hidden="true"></span>
        <span class="corner-bracket corner-br" aria-hidden="true"></span>

        <div class="panel-header">
            <div class="panel-title-area">
                <h2>
                    <span class="panel-icon-dot" aria-hidden="true"></span>
                    Los 10 meteoritos de mayor masa
                </h2>
                <p class="panel-desc">Especímenes más masivos registrados en el catálogo mundial (en gramos).</p>
            </div>
        </div>

        <div class="ranking-layout">
            <div class="table-wrap">
                <table aria-label="Ranking de los diez meteoritos con mayor masa">
                    <thead>
                        <tr>
                            <th scope="col">#</th>
                            <th scope="col">Meteorito</th>
                            <th scope="col">ID Oficial</th>
                            <th scope="col">Masa (g)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {ranking_filas}
                    </tbody>
                </table>
            </div>

            <aside class="mass-spotlight" id="ranking-spotlight" aria-label="Detalle del meteorito seleccionado">
                <div class="spotlight-header">
                    <span class="spotlight-eyebrow">Espectrometría de Masa</span>
                    <span class="spotlight-rank" id="spotlight-rank-val">{primer_lider['rank']}</span>
                </div>
                <h3 class="spotlight-name" id="spotlight-nombre-val">{primer_lider['name']}</h3>
                <div class="spotlight-id" id="spotlight-id-val">ID Catálogo NASA: {primer_lider['id']}</div>

                <div class="mass-grid">
                    <div class="mass-tile">
                        <span class="mass-tile-unit">Gramos (g)</span>
                        <span class="mass-tile-val" id="spotlight-g-val">{primer_lider['masa_g']} g</span>
                    </div>
                    <div class="mass-tile">
                        <span class="mass-tile-unit">Kilogramos (kg)</span>
                        <span class="mass-tile-val" id="spotlight-kg-val">{primer_lider['kg']}</span>
                    </div>
                    <div class="mass-tile">
                        <span class="mass-tile-unit">Toneladas Métricas (t)</span>
                        <span class="mass-tile-val" id="spotlight-ton-val">{primer_lider['ton']}</span>
                    </div>
                </div>

                <div class="spotlight-scale-wrap">
                    <div class="spotlight-scale-label">
                        <span>Escala relativa</span>
                        <span id="spotlight-scale-pct">{primer_lider['pct_rel']} respecto al líder</span>
                    </div>
                    <div class="spotlight-scale-track">
                        <div class="spotlight-scale-fill" id="spotlight-scale-bar" style="width:{primer_lider['pct_rel']};"></div>
                    </div>
                </div>
            </aside>
        </div>
    </section>

    <section class="panel" id="recientes">
        <span class="corner-bracket corner-tl" aria-hidden="true"></span>
        <span class="corner-bracket corner-tr" aria-hidden="true"></span>
        <span class="corner-bracket corner-bl" aria-hidden="true"></span>
        <span class="corner-bracket corner-br" aria-hidden="true"></span>

        <div class="panel-header">
            <div class="panel-title-area">
                <h2>
                    <span class="panel-icon-dot" aria-hidden="true"></span>
                    Últimos 10 registros del CSV
                </h2>
                <p class="panel-desc">
                    Permite auditar las incorporaciones recientes en el repositorio. Haz clic en una fila para ver la ficha completa.
                </p>
            </div>
        </div>

        <div class="recent-records-container">
            <div class="search-controls">
                <div class="search-input-wrapper">
                    <svg class="search-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                        <circle cx="11" cy="11" r="8"></circle>
                        <line x1="21" y1="21" x2="16.65" y2="16.65"></line>
                    </svg>
                    <input class="search-input" id="buscador" type="search"
                           placeholder="Buscar por nombre, ID o clase..."
                           aria-label="Buscar en los registros recientes">
                </div>
                <span id="filas-visibles" class="search-counter">10 de 10 registros visibles</span>
            </div>

            <!-- Minirradar orbital de coordenadas de impacto -->
            <div class="orbital-impact-map" aria-label="Mapa de telemetría de coordenadas">
                <div class="map-radar-area">
                    <svg class="map-svg-grid" viewBox="0 0 120 70" fill="none">
                        <line x1="0" y1="35" x2="120" y2="35" class="map-grid-line" stroke-dasharray="2 2" />
                        <line x1="60" y1="0" x2="60" y2="70" class="map-grid-line" stroke-dasharray="2 2" />
                        <circle cx="60" cy="35" r="30" stroke="rgba(0, 229, 255, 0.25)" stroke-width="0.8" />
                        <circle id="map-target-blip" class="map-target-blip" cx="60" cy="35" r="4" />
                    </svg>
                    <div class="map-telemetry-text" id="map-target-text">
                        <span class="map-telemetry-label">Radar de Coordenadas:</span> Pasa el cursor sobre un meteorito para triangular su posición terrestre.
                    </div>
                </div>
            </div>

            <div class="table-wrap">
                <table id="recientes-tabla" aria-label="Tabla de los últimos diez registros del catálogo">
                    <thead>
                        <tr>
                            <th scope="col">ID</th>
                            <th scope="col">Nombre</th>
                            <th scope="col">Clase</th>
                            <th scope="col">Masa (g)</th>
                            <th scope="col">Tipo</th>
                            <th scope="col">Año</th>
                            <th scope="col">Latitud</th>
                            <th scope="col">Longitud</th>
                        </tr>
                    </thead>
                    <tbody>
                        {recientes}
                    </tbody>
                </table>
            </div>
        </div>
    </section>

    <section class="panel" id="metodologia">
        <span class="corner-bracket corner-tl" aria-hidden="true"></span>
        <span class="corner-bracket corner-tr" aria-hidden="true"></span>
        <span class="corner-bracket corner-bl" aria-hidden="true"></span>
        <span class="corner-bracket corner-br" aria-hidden="true"></span>

        <div class="panel-header">
            <div class="panel-title-area">
                <h2>
                    <span class="panel-icon-dot" aria-hidden="true"></span>
                    Fuente, Metodología y Garantías CI/CD
                </h2>
                <p class="panel-desc">Gobernanza de datos abiertos e integridad de cálculos científicos.</p>
            </div>
        </div>
        <p>
            Los datos analizados proceden del conjunto público
            <a href="https://data.nasa.gov/dataset/meteorite-landings"
               target="_blank" rel="noopener noreferrer">
                Meteorite Landings — NASA Open Data
            </a>, compilado por The Meteoritical Society.
            La muestra inicial conserva las primeras 20.000 filas validadas de la fuente. El CSV versionado contiene actualmente {formato(total)} registros, incluidas las simulaciones educativas incorporadas durante las pruebas.
        </p>

        <div class="academic-notice">
            <strong>Aviso académico:</strong>
            los meteoritos ficticios que se incorporen para demostrar el funcionamiento
            de CI/CD son simulaciones educativas y no representan nuevos hallazgos reales de la NASA.
        </div>

        <p class="panel-desc">
            Tratamiento de valores faltantes: Los registros sin valor de masa disponible no se convierten en cero
            y son rigurosamente excluidos del cálculo de la media para evitar sesgos numéricos.
            Cada publicación exige superar 22 pruebas unitarias automatizadas y la validación estructural estricta.
        </p>
    </section>

    <footer>
        <p>
            Generado: <span>{seguro(fecha)}</span> ·
            Commit: <code>{seguro(commit)}</code>
        </p>
        <p>
            Proyecto académico · GitHub Actions · GitHub Pages · Observatorio de Meteoritos NASA
        </p>
    </footer>

</div>

<!-- Modal / Ficha Técnica Accesible -->
<div class="modal-overlay" id="modal-ficha" role="dialog" aria-modal="true" aria-hidden="true" aria-labelledby="modal-val-nombre">
    <div class="modal-sheet">
        <span class="corner-bracket corner-tl" aria-hidden="true"></span>
        <span class="corner-bracket corner-tr" aria-hidden="true"></span>
        <span class="corner-bracket corner-bl" aria-hidden="true"></span>
        <span class="corner-bracket corner-br" aria-hidden="true"></span>

        <div class="modal-top">
            <div>
                <div class="modal-eyebrow">Ficha Técnica de Muestra</div>
                <h3 class="modal-title" id="modal-val-nombre">Nombre de Meteorito</h3>
            </div>
            <button type="button" class="modal-close-btn" id="modal-cerrar-btn" aria-label="Cerrar ficha técnica">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                    <line x1="18" y1="6" x2="6" y2="18"></line>
                    <line x1="6" y1="6" x2="18" y2="18"></line>
                </svg>
            </button>
        </div>

        <div class="modal-telemetry-status">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
            <span>Registro verificado contra reglas de integridad CI/CD</span>
        </div>

        <div class="modal-fields-grid">
            <div class="modal-field">
                <div class="modal-field-label">Identificador NASA</div>
                <div class="modal-field-value" id="modal-val-id">-</div>
            </div>
            <div class="modal-field">
                <div class="modal-field-label">Clase Mineralógica</div>
                <div class="modal-field-value" id="modal-val-clase">-</div>
            </div>
            <div class="modal-field full-span">
                <div class="modal-field-label">Masa Medida</div>
                <div class="modal-field-value" id="modal-val-masa">-</div>
            </div>
            <div class="modal-field">
                <div class="modal-field-label">Tipo de Evento</div>
                <div class="modal-field-value" id="modal-val-tipo">-</div>
            </div>
            <div class="modal-field">
                <div class="modal-field-label">Año Registrado</div>
                <div class="modal-field-value" id="modal-val-anio">-</div>
            </div>
            <div class="modal-field full-span">
                <div class="modal-field-label">Coordenadas Geográficas</div>
                <div class="modal-field-value" id="modal-val-coord">-</div>
            </div>
        </div>
    </div>
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

    # Guardar también estilos y scripts separados para modularidad y desarrollo
    (carpeta_publica / "styles.css").write_text(ESTILOS.strip(), encoding="utf-8")
    (carpeta_publica / "app.js").write_text(JAVASCRIPT.strip(), encoding="utf-8")

    print("SITIO GENERADO CORRECTAMENTE")
    print(f"Registros procesados: {indicadores['total']}")
    print(f"Archivo HTML: {destino}")
    print(f"Commit: {commit}")


if __name__ == "__main__":
    main()
