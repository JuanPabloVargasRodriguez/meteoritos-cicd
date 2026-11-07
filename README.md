# Observatorio de Meteoritos NASA · CI/CD Pipeline

Sistema automatizado de integración y entrega continua (CI/CD) desarrollado en Python para validar, analizar y visualizar más de 20.000 registros del catálogo de meteoritos de la NASA (*The Meteoritical Society*), publicando automáticamente un panel estático interactivo en GitHub Pages.

---

## Características Principales

* **Integridad de Datos Rigurosa:** Validación estructural y semántica de 20.000 registros con reglas estrictas (identificadores únicos positivos, coordenadas en rangos geográficos válidos, años coherentes y verificación de valores numéricos finitos).
* **Cálculo Estadístico Científico:**
  * Indicadores de caídas (*Fell*) y hallazgos (*Found*).
  * Masa promedio calculada exclusivamente sobre valores registrados (sin imputar 0 a faltantes para evitar sesgos).
  * Auditoría de registros con información de masa no catalogada.
  * Top 10 clasificaciones mineralógicas más comunes.
  * Ranking de los 10 meteoritos más masivos registrados en la Tierra.
* **Interfaz de Observatorio Espacial:**
  * Estética de centro de control y monitoreo espacial (paleta oscura cósmica, líneas orbitales, badges de telemetría y baliza de estado en vivo).
  * Fondo dinámico de estrellas parpadeantes y meteoros en Canvas (respetando `@media (prefers-reduced-motion: reduce)`).
  * Tarjetas KPI interactivas con conteo ascendente y tooltips metodológicos accesibles.
  * Gráfico de barras interactivo con HUD de datos al pasar el cursor o navegar con teclado.
  * Donut comparativo *Fell* vs. *Found* con descripciones científicas.
  * Panel de espectrometría con equivalencias en gramos, kilogramos y toneladas métricas.
  * Buscador reactivo en los registros recientes con modal de inspección técnica (*Ficha de Meteorito*).
* **Pipeline CI/CD Automatizado:**
  * Ejecución de validación de datos.
  * 22 pruebas automatizadas con `pytest`.
  * Generación del sitio estático con inyección del commit SHA.
  * Despliegue automático a GitHub Pages.

---

## Estructura del Repositorio

```text
meteoritos-cicd/
├── .github/
│   └── workflows/
│       └── ci.yml             # Pipeline de GitHub Actions (Validación, Test y Despliegue)
├── datos/
│   └── meteoritos.csv         # Muestra de 20.000 registros validados de la NASA
├── public/                    # Archivos generados para publicación estática
│   ├── index.html             # Dashboard autónomo completo
│   ├── styles.css             # Estilos modulares del observatorio
│   └── app.js                 # Lógica interactiva accesible
├── scripts/
│   ├── analizar_datos.py      # Cálculo de métricas y filtros estadísticos
│   ├── generar_sitio.py       # Generador del sitio HTML/CSS/JS
│   ├── preparar_muestra.py    # Extracción y filtrado del dataset original
│   └── validar_datos.py       # Validación de tipos, rangos y consistencia
├── tests/
│   └── test_meteoritos.py     # 22 pruebas automatizadas con pytest
└── requirements.txt           # Dependencias del proyecto (pytest)
```

---

## Instalación y Ejecución Local

### 1. Clonar el repositorio y configurar el entorno
```bash
git clone https://github.com/tu-usuario/meteoritos-cicd.git
cd meteoritos-cicd
python -m venv .venv
# En Windows:
.venv\Scripts\activate
# En Linux/macOS:
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Validar los datos del CSV
Verifica que los 20.000 registros cumplan con las reglas de negocio:
```bash
python scripts/validar_datos.py
```

### 3. Ejecutar la suite de pruebas automatizadas
Ejecuta las 22 pruebas unitarias y de integración:
```bash
python -m pytest tests/ -v
```

### 4. Generar el dashboard estático
Genera los archivos listos para publicación en la carpeta `public/`:
```bash
python -m scripts.generar_sitio
```
Puedes abrir directamente el archivo `public/index.html` en cualquier navegador web.

---

## Guía para la Defensa en Clase

| Concepto Clave | Cómo Defenderlo |
| :--- | :--- |
| **Pipeline CI/CD** | Cada cambio en `main` dispara automáticamente el flujo en GitHub Actions. Si un registro en el CSV es inválido o falla una prueba unitaria, el despliegue a GitHub Pages se bloquea de inmediato, garantizando que nunca se publique información corrupta. |
| **Tratamiento de Faltantes** | Los meteoritos sin valor de masa registrado (70 registros en la muestra) no se convierten en cero, ya que distorsionarían la media hacia abajo. Se excluyen del promedio y se contabilizan explícitamente en una métrica de auditoría. |
| **Diferencia Fell vs. Found** | Solo un ~5,5% de los meteoritos corresponden a caídas observadas en tiempo real (*Fell*), mientras que más del 94% fueron descubiertos posteriormente en prospecciones geológicas (*Found*). |
| **Accesibilidad y Rendimiento** | Cero dependencias externas pesadas (sin React, sin D3 ni librerías de 20 MB). Código nativo accesible con teclado (<kbd>Tab</kbd>, <kbd>Enter</kbd>, <kbd>Esc</kbd>), roles ARIA y soporte total para `prefers-reduced-motion`. |
| **Seguridad** | Todos los valores provenientes del CSV son sanitizados con `html.escape` y serializados de forma protegida para evitar vulnerabilidades de Cross-Site Scripting (XSS). |

---

## Fuente de Datos
* **Conjunto de datos:** [Meteorite Landings — NASA Open Data](https://data.nasa.gov/dataset/meteorite-landings)
* **Compilación:** The Meteoritical Society
* **Aviso académico:** Los registros ficticios que se añadan para demostrar el funcionamiento del pipeline CI/CD son simulaciones educativas y no representan descubrimientos reales de la NASA.
